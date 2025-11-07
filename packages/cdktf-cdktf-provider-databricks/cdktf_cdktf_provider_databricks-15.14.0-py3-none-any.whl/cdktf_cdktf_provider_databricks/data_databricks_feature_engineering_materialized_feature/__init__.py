r'''
# `data_databricks_feature_engineering_materialized_feature`

Refer to the Terraform Registry for docs: [`data_databricks_feature_engineering_materialized_feature`](https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class DataDatabricksFeatureEngineeringMaterializedFeature(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringMaterializedFeature.DataDatabricksFeatureEngineeringMaterializedFeature",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature databricks_feature_engineering_materialized_feature}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        materialized_feature_id: builtins.str,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature databricks_feature_engineering_materialized_feature} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param materialized_feature_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#materialized_feature_id DataDatabricksFeatureEngineeringMaterializedFeature#materialized_feature_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb77d4fc12a98ccb6a7c7ae6e45cbd3fce46fc5b2327c015eb7b8fcbc0218b89)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksFeatureEngineeringMaterializedFeatureConfig(
            materialized_feature_id=materialized_feature_id,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DataDatabricksFeatureEngineeringMaterializedFeature resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksFeatureEngineeringMaterializedFeature to import.
        :param import_from_id: The id of the existing DataDatabricksFeatureEngineeringMaterializedFeature that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksFeatureEngineeringMaterializedFeature to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53c8c7416631182eff9ba94632e558bc37fc7506d97df7135c039ca2ed02fce0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="featureName")
    def feature_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "featureName"))

    @builtins.property
    @jsii.member(jsii_name="lastMaterializationTime")
    def last_materialization_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastMaterializationTime"))

    @builtins.property
    @jsii.member(jsii_name="offlineStoreConfig")
    def offline_store_config(
        self,
    ) -> "DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfigOutputReference":
        return typing.cast("DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfigOutputReference", jsii.get(self, "offlineStoreConfig"))

    @builtins.property
    @jsii.member(jsii_name="onlineStoreConfig")
    def online_store_config(
        self,
    ) -> "DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfigOutputReference":
        return typing.cast("DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfigOutputReference", jsii.get(self, "onlineStoreConfig"))

    @builtins.property
    @jsii.member(jsii_name="pipelineScheduleState")
    def pipeline_schedule_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineScheduleState"))

    @builtins.property
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @builtins.property
    @jsii.member(jsii_name="materializedFeatureIdInput")
    def materialized_feature_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "materializedFeatureIdInput"))

    @builtins.property
    @jsii.member(jsii_name="materializedFeatureId")
    def materialized_feature_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "materializedFeatureId"))

    @materialized_feature_id.setter
    def materialized_feature_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dcf31c3d2134929362e8fb76761acd52f9c0f29b040c6f08594131583080ca8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "materializedFeatureId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringMaterializedFeature.DataDatabricksFeatureEngineeringMaterializedFeatureConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "materialized_feature_id": "materializedFeatureId",
    },
)
class DataDatabricksFeatureEngineeringMaterializedFeatureConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        materialized_feature_id: builtins.str,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param materialized_feature_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#materialized_feature_id DataDatabricksFeatureEngineeringMaterializedFeature#materialized_feature_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19081d685f9718dc6be6dd666ad5e44fa167a1b22830e231f64135165dc834d8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument materialized_feature_id", value=materialized_feature_id, expected_type=type_hints["materialized_feature_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "materialized_feature_id": materialized_feature_id,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def materialized_feature_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#materialized_feature_id DataDatabricksFeatureEngineeringMaterializedFeature#materialized_feature_id}.'''
        result = self._values.get("materialized_feature_id")
        assert result is not None, "Required property 'materialized_feature_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringMaterializedFeatureConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringMaterializedFeature.DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfig",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_name": "catalogName",
        "schema_name": "schemaName",
        "table_name_prefix": "tableNamePrefix",
    },
)
class DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfig:
    def __init__(
        self,
        *,
        catalog_name: builtins.str,
        schema_name: builtins.str,
        table_name_prefix: builtins.str,
    ) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#catalog_name DataDatabricksFeatureEngineeringMaterializedFeature#catalog_name}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#schema_name DataDatabricksFeatureEngineeringMaterializedFeature#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#table_name_prefix DataDatabricksFeatureEngineeringMaterializedFeature#table_name_prefix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4a20c5ee3988d03f45f429d17f47d70227fac6372790ba075bbd172ff7044cb)
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
            check_type(argname="argument table_name_prefix", value=table_name_prefix, expected_type=type_hints["table_name_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "catalog_name": catalog_name,
            "schema_name": schema_name,
            "table_name_prefix": table_name_prefix,
        }

    @builtins.property
    def catalog_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#catalog_name DataDatabricksFeatureEngineeringMaterializedFeature#catalog_name}.'''
        result = self._values.get("catalog_name")
        assert result is not None, "Required property 'catalog_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schema_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#schema_name DataDatabricksFeatureEngineeringMaterializedFeature#schema_name}.'''
        result = self._values.get("schema_name")
        assert result is not None, "Required property 'schema_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name_prefix(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#table_name_prefix DataDatabricksFeatureEngineeringMaterializedFeature#table_name_prefix}.'''
        result = self._values.get("table_name_prefix")
        assert result is not None, "Required property 'table_name_prefix' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringMaterializedFeature.DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f95a3e7b4697e0d4eeb784e605616d91c0497456f8a61b70f77961218ccf7557)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="catalogNameInput")
    def catalog_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogNameInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaNameInput")
    def schema_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaNameInput"))

    @builtins.property
    @jsii.member(jsii_name="tableNamePrefixInput")
    def table_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNamePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="catalogName")
    def catalog_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalogName"))

    @catalog_name.setter
    def catalog_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70c7fecb05c66c210e7d42aaa92ae7cf9b95439b93bf879f365dd7fa4f0e670a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalogName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @schema_name.setter
    def schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9922aeee0163639bcc1e4f4febc24d964aa4feee55d3b9200a202a1b20403157)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tableNamePrefix")
    def table_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableNamePrefix"))

    @table_name_prefix.setter
    def table_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__feb8bd164ef8f53025a661ba3474477d48c21d5ac112ba4b35c0f078706a55a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableNamePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfig]:
        return typing.cast(typing.Optional[DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d3cbea31367fadd252324a1ed17cfb7f2239a30488e678f0322b711c6cb46c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringMaterializedFeature.DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfig",
    jsii_struct_bases=[],
    name_mapping={
        "capacity": "capacity",
        "name": "name",
        "read_replica_count": "readReplicaCount",
    },
)
class DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfig:
    def __init__(
        self,
        *,
        capacity: builtins.str,
        name: builtins.str,
        read_replica_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#capacity DataDatabricksFeatureEngineeringMaterializedFeature#capacity}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#name DataDatabricksFeatureEngineeringMaterializedFeature#name}.
        :param read_replica_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#read_replica_count DataDatabricksFeatureEngineeringMaterializedFeature#read_replica_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eff16a2c9f2d086472d7babf94352296d42b57659825d3003f1e57f66de419f7)
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument read_replica_count", value=read_replica_count, expected_type=type_hints["read_replica_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "capacity": capacity,
            "name": name,
        }
        if read_replica_count is not None:
            self._values["read_replica_count"] = read_replica_count

    @builtins.property
    def capacity(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#capacity DataDatabricksFeatureEngineeringMaterializedFeature#capacity}.'''
        result = self._values.get("capacity")
        assert result is not None, "Required property 'capacity' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#name DataDatabricksFeatureEngineeringMaterializedFeature#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def read_replica_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_materialized_feature#read_replica_count DataDatabricksFeatureEngineeringMaterializedFeature#read_replica_count}.'''
        result = self._values.get("read_replica_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringMaterializedFeature.DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2a77aa3d75300e07c170675c94464fb49eadc85ff043c4096491f44b19a1b39)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetReadReplicaCount")
    def reset_read_replica_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadReplicaCount", []))

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTime"))

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="capacityInput")
    def capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "capacityInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="readReplicaCountInput")
    def read_replica_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "readReplicaCountInput"))

    @builtins.property
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacity"))

    @capacity.setter
    def capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afe635c650b4d249e42f35ae713c2d47a8a5c124ab192c0e397230a76efc3fd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dea75714f87617e345d539df63ddbb84c50dcd6f5a275c9f1168cbfcc031fba6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="readReplicaCount")
    def read_replica_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "readReplicaCount"))

    @read_replica_count.setter
    def read_replica_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35969e85c5614bfcbd07e05665f306a41faa10ce5272a4afc1b91fb045e84b85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readReplicaCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfig]:
        return typing.cast(typing.Optional[DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__937b478dd948db70838a7d8b2229b8082ae2c9f6505b0276102174d2d234ef00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksFeatureEngineeringMaterializedFeature",
    "DataDatabricksFeatureEngineeringMaterializedFeatureConfig",
    "DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfig",
    "DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfigOutputReference",
    "DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfig",
    "DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfigOutputReference",
]

publication.publish()

def _typecheckingstub__eb77d4fc12a98ccb6a7c7ae6e45cbd3fce46fc5b2327c015eb7b8fcbc0218b89(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    materialized_feature_id: builtins.str,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53c8c7416631182eff9ba94632e558bc37fc7506d97df7135c039ca2ed02fce0(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dcf31c3d2134929362e8fb76761acd52f9c0f29b040c6f08594131583080ca8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19081d685f9718dc6be6dd666ad5e44fa167a1b22830e231f64135165dc834d8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    materialized_feature_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4a20c5ee3988d03f45f429d17f47d70227fac6372790ba075bbd172ff7044cb(
    *,
    catalog_name: builtins.str,
    schema_name: builtins.str,
    table_name_prefix: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f95a3e7b4697e0d4eeb784e605616d91c0497456f8a61b70f77961218ccf7557(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70c7fecb05c66c210e7d42aaa92ae7cf9b95439b93bf879f365dd7fa4f0e670a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9922aeee0163639bcc1e4f4febc24d964aa4feee55d3b9200a202a1b20403157(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__feb8bd164ef8f53025a661ba3474477d48c21d5ac112ba4b35c0f078706a55a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d3cbea31367fadd252324a1ed17cfb7f2239a30488e678f0322b711c6cb46c0(
    value: typing.Optional[DataDatabricksFeatureEngineeringMaterializedFeatureOfflineStoreConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eff16a2c9f2d086472d7babf94352296d42b57659825d3003f1e57f66de419f7(
    *,
    capacity: builtins.str,
    name: builtins.str,
    read_replica_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2a77aa3d75300e07c170675c94464fb49eadc85ff043c4096491f44b19a1b39(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afe635c650b4d249e42f35ae713c2d47a8a5c124ab192c0e397230a76efc3fd5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dea75714f87617e345d539df63ddbb84c50dcd6f5a275c9f1168cbfcc031fba6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35969e85c5614bfcbd07e05665f306a41faa10ce5272a4afc1b91fb045e84b85(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__937b478dd948db70838a7d8b2229b8082ae2c9f6505b0276102174d2d234ef00(
    value: typing.Optional[DataDatabricksFeatureEngineeringMaterializedFeatureOnlineStoreConfig],
) -> None:
    """Type checking stubs"""
    pass
