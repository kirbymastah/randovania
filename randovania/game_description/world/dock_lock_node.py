from __future__ import annotations

import dataclasses
from typing import Iterator

from randovania.game_description.requirements.base import Requirement
from randovania.game_description.resources.node_resource_info import NodeResourceInfo
from randovania.game_description.resources.resource_info import ResourceInfo, ResourceGain
from randovania.game_description.world.dock_node import DockNode
from randovania.game_description.world.node import NodeContext, Node
from randovania.game_description.world.node_identifier import NodeIdentifier
from randovania.game_description.world.resource_node import ResourceNode


@dataclasses.dataclass(frozen=True, slots=True)
class DockLockNode(ResourceNode):
    dock: DockNode

    @classmethod
    def create_from_dock(cls, dock: DockNode) -> DockLockNode:
        lock_identifier = dock.lock_node_identifier
        return DockLockNode(
            identifier=lock_identifier,
            heal=False,
            location=None,
            description="",
            layers=dock.layers,
            extra={},
            dock=dock,
        )

    def __repr__(self):
        return "DockLockNode({!r} -> {})".format(self.name, self.dock.name)

    def resource(self, context: NodeContext) -> ResourceInfo:
        return NodeResourceInfo.from_node(self.dock, context)

    def can_collect(self, context: NodeContext) -> bool:
        dock = self.dock

        front_weak = dock.get_front_weakness(context)
        if not context.has_resource(self.resource(context)):
            if front_weak.lock is not None:
                return True

        dock_target = dock.get_target_identifier(context)
        target = context.node_provider.node_by_identifier(dock_target)
        if not context.has_resource(NodeResourceInfo.from_node(target, context)):
            if front_weak.can_unlock_from_back(dock.get_back_weakness(context)):
                return True

        return False

    def is_collected(self, context: NodeContext) -> bool:
        return not self.can_collect(context)

    def resource_gain_on_collect(self, context: NodeContext) -> ResourceGain:
        dock = self.dock
        dock_target = dock.get_target_identifier(context)
        dock_resource = self.resource(context)
        target_resource = NodeResourceInfo.from_node(context.node_provider.node_by_identifier(dock_target), context)

        front_weak = dock.get_front_weakness(context)
        if not context.has_resource(dock_resource) and front_weak.lock is not None:
            yield dock_resource, 1

        if not context.has_resource(target_resource) and front_weak.can_unlock_from_back(dock.get_back_weakness(context)):
            yield target_resource, 1

    def connections_from(self, context: NodeContext) -> Iterator[tuple[Node, Requirement]]:
        dock = self.dock
        target_identifier = dock.get_target_identifier(context)
        if target_identifier is not None and dock._lock_connection(context) is not None:
            yield dock, Requirement.trivial()

    @property
    def is_derived_node(self) -> bool:
        return True
