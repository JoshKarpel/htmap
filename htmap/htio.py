# Copyright 2018 HTCondor Team, Computer Sciences Department,
# University of Wisconsin-Madison, WI.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gzip
import json
import logging
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, List

import cloudpickle
import htcondor

from . import names
from .types import ARGS_AND_KWARGS

logger = logging.getLogger(__name__)


def save_object(obj: Any, path: Path) -> None:
    """Serialize a Python object (including "objects", like functions) to a file at the given ``path``."""
    with gzip.open(path, mode="wb") as file:
        cloudpickle.dump(obj, file)


def load_object(path: Path) -> Any:
    """Deserialize an object from the file at the given ``path``."""
    with gzip.open(path, mode="rb") as file:
        return cloudpickle.load(file)


def load_objects(path: Path) -> Iterator[Any]:
    """Deserialize a stream of objects from the file at the given ``path``."""
    with gzip.open(path, mode="rb") as file:
        while True:
            yield cloudpickle.load(file)


def save_func(map_dir: Path, func: Callable) -> None:
    """Save the mapped function to the map directory."""
    path = map_dir / names.FUNC
    save_object(func, path)

    logger.debug(f"Saved function to {path}")


def save_inputs(map_dir: Path, args_and_kwargs: Iterable[ARGS_AND_KWARGS],) -> None:
    """
    Save the arguments to the mapped function to the map's input directory.
    """
    base_path = map_dir / names.INPUTS_DIR
    for component, a_and_k in enumerate(args_and_kwargs):
        save_object(a_and_k, base_path / f"{component}.{names.INPUT_EXT}")

    logger.debug(f"Saved args and kwargs in {base_path}")


def save_num_components(map_dir: Path, num_components: int) -> None:
    """Save the number of components in a map."""
    path = _num_components_path(map_dir)
    path.write_text(str(num_components))


def load_num_components(map_dir: Path) -> int:
    """Load the number of components in a map."""
    path = _num_components_path(map_dir)
    return int(path.read_text())


def _num_components_path(map_dir: Path) -> Path:
    return map_dir / names.NUM_COMPONENTS


def append_cluster_id(map_dir: Path, cluster_id: int) -> None:
    """Add a cluster ID to a map."""
    with _cluster_ids_path(map_dir).open(mode="a") as file:
        file.write(str(cluster_id) + "\n")


def load_cluster_ids(map_dir: Path) -> List[int]:
    """Load the cluster IDs for a map."""
    return [int(cid.strip()) for cid in _cluster_ids_path(map_dir).read_text().splitlines()]


def _cluster_ids_path(map_dir: Path) -> Path:
    return map_dir / names.CLUSTER_IDS


def save_submit(map_dir: Path, submit: htcondor.Submit) -> None:
    """Save a dictionary that represents the map's :class:`htcondor.Submit` object."""
    path = _submit_path(map_dir)
    with path.open(mode="w") as f:
        json.dump(
            dict(submit), f, indent=4, separators=(", ", ": "),
        )

    logger.debug(f"Saved submit object to {path}")


def load_submit(map_dir: Path) -> htcondor.Submit:
    """Load an :class:`htcondor.Submit` object that was saved using :func:`save_submit`."""
    with _submit_path(map_dir).open(mode="r") as f:
        return htcondor.Submit(json.load(f))


def _submit_path(map_dir: Path) -> Path:
    return map_dir / names.SUBMIT


def save_itemdata(map_dir: Path, itemdata: List[dict]) -> None:
    """Save the map's itemdata as a list of JSON dictionaries."""
    path = _itemdata_path(map_dir)
    with path.open(mode="w") as f:
        json.dump(
            itemdata, f, indent=None, separators=(",", ":"),
        )  # most compact representation

    logger.debug(f"Saved itemdata to {path}")


def load_itemdata(map_dir: Path) -> List[dict]:
    """Load itemdata that was saved using :func:`save_itemdata`."""
    with _itemdata_path(map_dir).open(mode="r") as f:
        return json.load(f)


def _itemdata_path(map_dir: Path) -> Path:
    return map_dir / names.ITEMDATA
