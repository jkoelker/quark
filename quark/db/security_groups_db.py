# Copyright 2013 Openstack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# Justin todo:
# - recreate the security groups DB schema for quark
# - recreate the SG interface for quark

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext import declarative

from quantum.db import models_v2 as models
from quantum.openstack.common import log as logging

from quark.db.models import BASEV2

HasId = models.HasId

LOG = logging.getLogger("quantum.quark.db.security_groups_db")


port_security_group_association_table = sa.Table(
    "quark_port_security_group_associations",
    BASEV2.metadata,
    sa.Column("port_id", sa.String(36),
              sa.ForeignKey("quark_ports.id")),
    sa.Column("security_group_id", sa.String(36),
              sa.ForeignKey("quark_security_groups.id")))


class SecurityGroupRule(BASEV2, models.HasId, models.HasTenant):
    __tablename__ = "quark_security_group_rules"
    group_id = sa.Column(sa.String(36),
                         sa.ForeignKey("quark.security_groups.id"),
                         nullable=False)


class SecurityGroup(BASEV2, models.HasId, models.HasTenant):
    __tablename__ = "quark_security_groups"
    name = sa.Column(sa.String(32), nullable=False)
    description = sa.Column(sa.String(128), nullable=False)
    rules = orm.relationship(SecurityGroupRule, backref="group")

    @declarative.declared_attr
    def ports(cls):
        jointable = port_security_group_association_table
        primaryjoin = cls.id == jointable.c.security_group_id
        secondaryjoin = (jointable.c.port_id == models.Port.id)
        return orm.relationship(models.Port, primaryjoin=primaryjoin,
                                secondaryjoin=secondaryjoin,
                                secondary=jointable,
                                backref="security_groups")
