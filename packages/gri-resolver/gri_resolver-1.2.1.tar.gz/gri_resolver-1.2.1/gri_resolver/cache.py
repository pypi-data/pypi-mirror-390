from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading


@dataclass
class CacheEntry:
    item_id: str
    image_path: Path


class CacheIndex:
    def __init__(self, root: Path):
        self.root = root
        self.manifest = root / "manifest.json"
        # Index format: item_id -> {"path": str, "tile": str, "quality_score": float, "metadata": Dict}
        # Or legacy format: item_id -> str (path only)
        self._index: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        if self.manifest.exists():
            try:
                raw_index = json.loads(self.manifest.read_text())
                # Migrate legacy format (item_id -> str) to new format
                self._index = {}
                for item_id, value in raw_index.items():
                    if isinstance(value, str):
                        # Legacy format: just a path string
                        self._index[item_id] = {"path": value, "tile": None, "quality_score": 0.0, "metadata": {}}
                    elif isinstance(value, dict):
                        # New format: ensure all fields are present
                        self._index[item_id] = {
                            "path": value.get("path", ""),
                            "tile": value.get("tile"),
                            "quality_score": value.get("quality_score", 0.0),
                            "user_rating": value.get("user_rating"),
                            "metadata": value.get("metadata", {}),
                        }
                    else:
                        # Invalid format, skip
                        continue
            except Exception:
                self._index = {}

    def reload(self) -> None:
        """Reload the cache manifest from disk."""
        with self._lock:
            self._load()

    def _save(self) -> None:
        self.manifest.write_text(json.dumps(self._index, indent=2))

    def get(self, item_id: str) -> Optional[Path]:
        """Get cached path for an item by item_id (legacy method, kept for compatibility)."""
        with self._lock:
            entry = self._index.get(item_id)
            if entry is None:
                return None
            if isinstance(entry, str):
                # Legacy format
                return Path(entry)
            # New format
            path_str = entry.get("path")
            return Path(path_str) if path_str else None

    def put(
        self,
        item_id: str,
        image_path: Path,
        tile_code: Optional[str] = None,
        quality_score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store an item in the cache with optional quality metadata.

        Args:
            item_id: Unique identifier for the item
            image_path: Path to the cached image file
            tile_code: MGRS tile code (e.g., "31UDQ")
            quality_score: Quality score for this item (higher = better)
            metadata: Additional metadata dictionary
        """
        with self._lock:
            # Preserve existing user_rating if present
            existing_entry = self._index.get(item_id, {})
            existing_rating = existing_entry.get("user_rating") if isinstance(existing_entry, dict) else None

            self._index[item_id] = {
                "path": str(image_path),
                "tile": tile_code,
                "quality_score": quality_score,
                "user_rating": existing_rating,
                "metadata": metadata or {},
            }
            self._save()

    def get_best_for_tile(self, tile_code: str) -> Optional[Path]:
        """Get the best cached image for a given tile.

        Selection priority:
        1. User rating (if any image has a user_rating, prefer the highest rated)
        2. Quality score (fallback when no user ratings exist)

        Args:
            tile_code: MGRS tile code (e.g., "31UDQ")

        Returns:
            Path to the best image, or None if no cached images for this tile
        """
        with self._lock:
            best_entry = None
            best_rating = None  # None means no user rating
            best_score = float("-inf")

            for item_id, entry in self._index.items():
                if isinstance(entry, str):
                    # Legacy format: can't determine tile, skip
                    continue

                entry_tile = entry.get("tile")
                if entry_tile == tile_code:
                    # Skip images in QI_DATA directory (not exploitable images)
                    path_str = entry.get("path")
                    if self._is_qi_data_path(path_str):
                        continue

                    user_rating = entry.get("user_rating")
                    quality_score = entry.get("quality_score", 0.0)

                    # Priority 1: Prefer images with user_rating
                    if user_rating is not None:
                        if best_rating is None:
                            # First image with user_rating, prefer it
                            best_entry = entry
                            best_rating = user_rating
                            best_score = quality_score
                        elif user_rating > best_rating:
                            # Higher user_rating, prefer it
                            best_entry = entry
                            best_rating = user_rating
                            best_score = quality_score
                        elif user_rating == best_rating and quality_score > best_score:
                            # Same user_rating, prefer higher quality_score
                            best_entry = entry
                            best_score = quality_score
                    elif best_rating is None:
                        # No user_rating for this image, and we haven't found any with rating
                        # Use quality_score as fallback
                        if quality_score > best_score:
                            best_score = quality_score
                            best_entry = entry

            if best_entry:
                path_str = best_entry.get("path")
                return Path(path_str) if path_str else None
            return None

    def get_all_for_tile(self, tile_code: str) -> List[Dict[str, Any]]:
        """Get all cached entries for a given tile, sorted by best first.

        Args:
            tile_code: MGRS tile code (e.g., "31UDQ")

        Returns:
            List of cache entries (dicts with path, quality_score, metadata, etc.),
            sorted with best first (user_rating prioritized, then quality_score)
        """
        with self._lock:
            results = []
            for item_id, entry in self._index.items():
                if isinstance(entry, str):
                    # Legacy format: can't determine tile, skip
                    continue

                entry_tile = entry.get("tile")
                if entry_tile == tile_code:
                    # Skip entries without a valid path (orphaned entries)
                    path_str = entry.get("path")
                    if not path_str:
                        continue
                    # Skip images in QI_DATA directory (not exploitable images)
                    if self._is_qi_data_path(path_str):
                        continue
                    result = dict(entry)
                    result["item_id"] = item_id
                    results.append(result)

            # Sort: prioritize user_rating, then quality_score
            # Images with user_rating come first, sorted by rating (descending)
            # Then images without user_rating, sorted by quality_score (descending)
            def sort_key(x: Dict[str, Any]) -> tuple:
                user_rating = x.get("user_rating")
                quality_score = x.get("quality_score", 0.0)
                # Return tuple: (has_rating: bool, rating/score, quality_score)
                # This ensures: (True, high_rating, ...) > (True, low_rating, ...)
                # > (False, ..., high_score) > (False, ..., low_score)
                if user_rating is not None:
                    return (True, user_rating, quality_score)
                else:
                    return (False, 0.0, quality_score)

            results.sort(key=sort_key, reverse=True)
            return results

    def rate_item(self, item_id: str, rating: float) -> bool:
        """Rate an item with a user rating.

        Args:
            item_id: Unique identifier for the item
            rating: User rating (typically 0.0 to 5.0, or None to remove rating)

        Returns:
            True if the item was found and rated, False otherwise
        """
        with self._lock:
            entry = self._index.get(item_id)
            if entry is None:
                return False
            if isinstance(entry, str):
                # Legacy format: convert to new format
                self._index[item_id] = {
                    "path": entry,
                    "tile": None,
                    "quality_score": 0.0,
                    "user_rating": rating,
                    "metadata": {},
                }
            else:
                # New format: update rating
                entry["user_rating"] = rating
            self._save()
            return True

    def delete_item(self, item_id: str) -> Optional[str]:
        """Delete an item from the cache and remove the associated file and preview.

        Also removes empty directories up to the tile directory.

        Args:
            item_id: Unique identifier for the item

        Returns:
            Path to the deleted file if successful, None if item not found
        """
        with self._lock:
            entry = self._index.get(item_id)
            if entry is None:
                return None

            # Get the file path and tile code
            if isinstance(entry, str):
                file_path = Path(entry)
                tile_code = None
            else:
                path_str = entry.get("path")
                if not path_str:
                    return None
                file_path = Path(path_str)
                tile_code = entry.get("tile")

            # Remove from index
            del self._index[item_id]
            self._save()

            # Try to delete the file
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass  # Continue even if file deletion fails

            # Delete associated preview if it exists
            try:
                preview_path = file_path.parent / f"{file_path.stem}.preview.jpg"
                if preview_path.exists():
                    preview_path.unlink()
            except Exception:
                pass  # Continue even if preview deletion fails

            # Find the .SAFE directory (product root) containing this file
            safe_dir = self._find_safe_directory(file_path)
            if safe_dir:
                # Check if there are other images from the same SAFE product
                has_other_images = False
                for other_item_id, other_entry in self._index.items():
                    if other_item_id == item_id:
                        continue
                    other_path_str = None
                    if isinstance(other_entry, str):
                        other_path_str = other_entry
                    elif isinstance(other_entry, dict):
                        other_path_str = other_entry.get("path")
                    if other_path_str:
                        try:
                            other_path = Path(other_path_str)
                            # Check if the other file is in the same SAFE directory
                            other_safe_dir = self._find_safe_directory(other_path)
                            if other_safe_dir == safe_dir:
                                has_other_images = True
                                break
                        except Exception:
                            pass

                # If no other images in this SAFE product, remove the entire SAFE directory
                if not has_other_images and safe_dir.exists():
                    try:
                        shutil.rmtree(safe_dir)
                    except Exception:
                        pass  # Continue even if directory deletion fails
                elif tile_code:
                    # If other images exist, just remove empty directories up to tile directory
                    self._remove_empty_dirs_up_to_tile(file_path.parent, tile_code)
            elif tile_code:
                # Fallback: if no .SAFE directory found, use the old method
                product_dir = file_path.parent
                has_other_images = False
                if product_dir.exists():
                    for other_item_id, other_entry in self._index.items():
                        if other_item_id == item_id:
                            continue
                        other_path_str = None
                        if isinstance(other_entry, str):
                            other_path_str = other_entry
                        elif isinstance(other_entry, dict):
                            other_path_str = other_entry.get("path")
                        if other_path_str:
                            try:
                                other_path = Path(other_path_str)
                                if other_path.parent == product_dir:
                                    has_other_images = True
                                    break
                            except Exception:
                                pass

                if not has_other_images and product_dir.exists():
                    try:
                        shutil.rmtree(product_dir)
                    except Exception:
                        pass
                else:
                    self._remove_empty_dirs_up_to_tile(file_path.parent, tile_code)

            return str(file_path)

    def delete_tile(self, tile_code: str) -> Dict[str, Any]:
        """Delete all items for a given tile from the cache and remove associated files and previews.

        Also removes empty directories up to the tile directory.

        Args:
            tile_code: MGRS tile code (e.g., "31UDQ")

        Returns:
            Dictionary with deleted_count, deleted_files, and failed_files
        """
        deleted_count = 0
        deleted_files: List[str] = []
        failed_files: List[str] = []
        product_dirs_to_remove: set = set()

        with self._lock:
            # Find all items for this tile
            items_to_delete = []
            for item_id, entry in self._index.items():
                if isinstance(entry, str):
                    continue  # Legacy format, can't determine tile

                entry_tile = entry.get("tile")
                if entry_tile == tile_code:
                    items_to_delete.append((item_id, entry))

        # Delete each item
        for item_id, entry in items_to_delete:
            # Remove from index first (even if file path is missing)
            with self._lock:
                del self._index[item_id]
            deleted_count += 1

            # Get the file path
            file_path = None
            if isinstance(entry, str):
                file_path = Path(entry)
            else:
                path_str = entry.get("path")
                if path_str:
                    file_path = Path(path_str)

            # If we have a valid file path, try to delete the file
            if file_path:
                # Find the .SAFE directory (product root) containing this file
                safe_dir = self._find_safe_directory(file_path)
                if safe_dir:
                    # Track SAFE directory for cleanup (will remove entire directory including GRANULE, QI_DATA, etc.)
                    product_dirs_to_remove.add(safe_dir)
                else:
                    # Fallback: use parent directory if no .SAFE found
                    product_dirs_to_remove.add(file_path.parent)

                # Try to delete the file
                try:
                    if file_path.exists():
                        file_path.unlink()
                        deleted_files.append(str(file_path))
                    else:
                        deleted_files.append(str(file_path))  # Still count as deleted even if file doesn't exist
                except Exception:
                    failed_files.append(str(file_path))

                # Delete associated preview if it exists
                try:
                    preview_path = file_path.parent / f"{file_path.stem}.preview.jpg"
                    if preview_path.exists():
                        preview_path.unlink()
                except Exception:
                    pass  # Continue even if preview deletion fails
            else:
                # Entry had no path, but we still removed it from index
                # Count it as deleted (orphaned entry)
                deleted_files.append(f"{item_id} (no path)")

        if deleted_count > 0:
            with self._lock:
                self._save()

        # Remove product directories completely (including QI_DATA and other subdirectories)
        for product_dir in product_dirs_to_remove:
            if product_dir.exists():
                try:
                    shutil.rmtree(product_dir)
                except Exception:
                    pass  # Continue even if directory deletion fails

        # Find and remove the tile directory if it's empty
        # Try to find the tile directory from any deleted file path
        tile_dir = None
        for item_id, entry in items_to_delete:
            path_str = None
            if isinstance(entry, str):
                path_str = entry
            elif isinstance(entry, dict):
                path_str = entry.get("path")
            if path_str:
                try:
                    file_path = Path(path_str)
                    # Find the tile directory by walking up from the file path
                    current = file_path.resolve()
                    while current and current.exists():
                        if current.name == tile_code and current.is_dir():
                            tile_dir = current
                            break
                        parent = current.parent
                        if parent == current or not parent:
                            break
                        current = parent
                    if tile_dir:
                        break  # Found it, no need to continue
                except Exception:
                    continue

        # Remove the tile directory if it exists and is empty (or only contains empty subdirectories)
        if tile_dir and tile_dir.exists():
            try:
                if self._is_dir_empty(tile_dir):
                    # Directory is empty, remove it recursively
                    shutil.rmtree(tile_dir)
            except Exception:
                pass  # Continue even if directory deletion fails

        # Also try to remove empty directories up to the tile directory as fallback
        # (in case some directories weren't tracked in product_dirs_to_remove)
        for product_dir in product_dirs_to_remove:
            self._remove_empty_dirs_up_to_tile(product_dir, tile_code)

        return {
            "deleted_count": deleted_count,
            "deleted_files": deleted_files,
            "failed_files": failed_files,
        }

    def _find_safe_directory(self, file_path: Path) -> Optional[Path]:
        """Find the .SAFE directory containing the given file path.

        Args:
            file_path: Path to a file (image) within a SAFE product structure

        Returns:
            Path to the .SAFE directory, or None if not found
        """
        current = Path(file_path).resolve()
        # Walk up the directory tree looking for a .SAFE directory
        while current and current.exists():
            if current.name.endswith('.SAFE') and current.is_dir():
                return current
            parent = current.parent
            # Stop if we've reached the root or if parent is the same
            if parent == current or not parent:
                break
            current = parent
        return None

    def _is_qi_data_path(self, path_str: str) -> bool:
        """Check if a path is in a QI_DATA directory (not exploitable images).

        Args:
            path_str: Path string to check

        Returns:
            True if the path is in QI_DATA directory, False otherwise
        """
        if not path_str:
            return False
        path_lower = path_str.lower()
        return "/qi_data/" in path_lower or "/qi_data\\" in path_lower or "\\qi_data\\" in path_lower

    def _is_dir_empty(self, dir_path: Path) -> bool:
        """Check if a directory is empty, including empty subdirectories.

        Args:
            dir_path: Path to the directory to check

        Returns:
            True if the directory is empty (no files, only empty subdirectories), False otherwise
        """
        try:
            items = list(dir_path.iterdir())
            if not items:
                return True
            # Check if all items are empty directories
            for item in items:
                if item.is_file():
                    return False
                if item.is_dir():
                    if not self._is_dir_empty(item):
                        return False
            return True
        except Exception:
            return False

    def _remove_empty_dirs_up_to_tile(self, start_dir: Path, tile_code: str) -> None:
        """Remove empty directories starting from start_dir up to (and including) the tile directory.

        Args:
            start_dir: Starting directory path (parent of deleted file)
            tile_code: MGRS tile code (e.g., "31UDQ")
        """
        try:
            current = Path(start_dir).resolve()
            # Find the tile directory by looking for a directory named with the tile code
            # The structure is typically: outputs/TILE_CODE/.../file
            tile_dir_name = tile_code

            # Walk up the directory tree
            while current and current.exists():
                # Check if this is the tile directory
                is_tile_dir = current.name == tile_dir_name

                # Try to remove the directory if it's empty
                try:
                    # Check if directory is empty (no files, only empty subdirectories are OK to remove)
                    if current.is_dir():
                        # List all items in the directory
                        items = list(current.iterdir())
                        if not items:
                            # Directory is empty, remove it
                            current.rmdir()
                            # If this was the tile directory, stop here
                            if is_tile_dir:
                                break
                        else:
                            # Directory is not empty, stop here
                            break
                except OSError:
                    # Can't remove (not empty, permission error, etc.), stop here
                    break

                # Move to parent directory
                parent = current.parent
                # Stop if we've reached the root or if parent is the same (shouldn't happen)
                if parent == current or not parent:
                    break
                current = parent
        except Exception:
            # Silently ignore errors in directory cleanup
            pass

    def get_image_info(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get all information about a cached image.

        Args:
            item_id: Unique identifier for the item

        Returns:
            Dictionary with all image information (path, tile, quality_score, user_rating, metadata)
            or None if item not found
        """
        with self._lock:
            entry = self._index.get(item_id)
            if entry is None:
                return None

            if isinstance(entry, str):
                # Legacy format
                return {
                    "item_id": item_id,
                    "path": entry,
                    "tile": None,
                    "quality_score": 0.0,
                    "user_rating": None,
                    "metadata": {},
                }

            # New format
            result = dict(entry)
            result["item_id"] = item_id
            # Ensure all fields are present
            result.setdefault("user_rating", None)
            result.setdefault("metadata", {})
            return result

    def list_all_tiles(self) -> Dict[str, Dict[str, Any]]:
        """List all tiles with their statistics.

        Returns:
            Dictionary mapping tile_code to statistics (image_count, best_score, top_rated_item_id)
        """
        tiles_dict: Dict[str, Dict[str, Any]] = {}

        with self._lock:
            for item_id, entry in self._index.items():
                if isinstance(entry, str):
                    continue
                tile_code = entry.get("tile")
                if not tile_code:
                    continue

                # Skip entries without a valid path (orphaned entries)
                path_str = entry.get("path")
                if not path_str:
                    continue

                # Skip images in QI_DATA directory (not exploitable images)
                path_lower = path_str.lower()
                if "/qi_data/" in path_lower or "/qi_data\\" in path_lower or "\\qi_data\\" in path_lower:
                    continue

                if tile_code not in tiles_dict:
                    tiles_dict[tile_code] = {
                        "tile_code": tile_code,
                        "image_count": 0,
                        "best_score": float("-inf"),
                        "top_rated_item_id": None,
                        "top_rated_score": None,
                    }

                tiles_dict[tile_code]["image_count"] += 1
                score = entry.get("quality_score", 0.0)
                if score > tiles_dict[tile_code]["best_score"]:
                    tiles_dict[tile_code]["best_score"] = score

                # Track top rated image (by user_rating, fallback to quality_score)
                user_rating = entry.get("user_rating")
                current_top_rating = tiles_dict[tile_code]["top_rated_score"]
                current_top_item_id = tiles_dict[tile_code]["top_rated_item_id"]

                # Check if current top has user_rating
                current_has_user_rating = False
                if current_top_item_id:
                    current_entry = self._index.get(current_top_item_id)
                    if isinstance(current_entry, dict):
                        current_has_user_rating = current_entry.get("user_rating") is not None

                # Prefer user_rating over quality_score
                if user_rating is not None:
                    # This image has user_rating
                    if not current_has_user_rating:
                        # Current top doesn't have user_rating, prefer this one
                        tiles_dict[tile_code]["top_rated_item_id"] = item_id
                        tiles_dict[tile_code]["top_rated_score"] = user_rating
                    elif current_top_rating is not None and user_rating > current_top_rating:
                        # Both have user_rating, pick the higher one
                        tiles_dict[tile_code]["top_rated_item_id"] = item_id
                        tiles_dict[tile_code]["top_rated_score"] = user_rating
                elif not current_has_user_rating:
                    # No user_rating for this image, and current top also has no user_rating
                    # Use quality_score as fallback
                    top_score = tiles_dict[tile_code].get("top_rated_score", float("-inf"))
                    if current_top_item_id is None or score > top_score:
                        tiles_dict[tile_code]["top_rated_item_id"] = item_id
                        tiles_dict[tile_code]["top_rated_score"] = score

        return tiles_dict

    def cleanup(self) -> Dict[str, Any]:
        """Remove cache entries for files that no longer exist on disk.

        Returns:
            Dictionary with cleanup statistics: removed_count, removed_items
        """
        removed_count = 0
        removed_items: List[str] = []

        with self._lock:
            items_to_remove = []
            for item_id, entry in self._index.items():
                # Get file path
                if isinstance(entry, str):
                    file_path = Path(entry)
                else:
                    path_str = entry.get("path")
                    if not path_str:
                        # Entry has no path, remove it
                        items_to_remove.append(item_id)
                        continue
                    file_path = Path(path_str)

                # Check if file exists
                if not file_path.exists():
                    items_to_remove.append(item_id)

            # Remove invalid entries
            for item_id in items_to_remove:
                del self._index[item_id]
                removed_count += 1
                removed_items.append(item_id)

            # Save updated manifest if any entries were removed
            if removed_count > 0:
                self._save()

        return {
            "removed_count": removed_count,
            "removed_items": removed_items,
        }
