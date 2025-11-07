r'''
# `data_databricks_feature_engineering_feature`

Refer to the Terraform Registry for docs: [`data_databricks_feature_engineering_feature`](https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature).
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


class DataDatabricksFeatureEngineeringFeature(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeature",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature databricks_feature_engineering_feature}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        full_name: builtins.str,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature databricks_feature_engineering_feature} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#full_name DataDatabricksFeatureEngineeringFeature#full_name}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3696c21da7bde97eef80dcada822c535ddaab0edcbb1e4eb8d43380d1642286)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksFeatureEngineeringFeatureConfig(
            full_name=full_name,
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
        '''Generates CDKTF code for importing a DataDatabricksFeatureEngineeringFeature resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksFeatureEngineeringFeature to import.
        :param import_from_id: The id of the existing DataDatabricksFeatureEngineeringFeature that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksFeatureEngineeringFeature to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf501f315949e3e858c2e5f0ec5b124e8c2e5d9cab0eb90a4e0b284644c4173d)
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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="filterCondition")
    def filter_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filterCondition"))

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(
        self,
    ) -> "DataDatabricksFeatureEngineeringFeatureFunctionOutputReference":
        return typing.cast("DataDatabricksFeatureEngineeringFeatureFunctionOutputReference", jsii.get(self, "function"))

    @builtins.property
    @jsii.member(jsii_name="inputs")
    def inputs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "inputs"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "DataDatabricksFeatureEngineeringFeatureSourceOutputReference":
        return typing.cast("DataDatabricksFeatureEngineeringFeatureSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="timeWindow")
    def time_window(
        self,
    ) -> "DataDatabricksFeatureEngineeringFeatureTimeWindowOutputReference":
        return typing.cast("DataDatabricksFeatureEngineeringFeatureTimeWindowOutputReference", jsii.get(self, "timeWindow"))

    @builtins.property
    @jsii.member(jsii_name="fullNameInput")
    def full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="fullName")
    def full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullName"))

    @full_name.setter
    def full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7058d7db513a7dcdf5a801f30d0d0b26af9a4c8afe70fe403afe6e62a06914e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fullName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "full_name": "fullName",
    },
)
class DataDatabricksFeatureEngineeringFeatureConfig(
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
        full_name: builtins.str,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#full_name DataDatabricksFeatureEngineeringFeature#full_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0997a45d89fb01f308fdec91b6ec0788a53aa1617788db94dbe19d24ff86b3d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument full_name", value=full_name, expected_type=type_hints["full_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "full_name": full_name,
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
    def full_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#full_name DataDatabricksFeatureEngineeringFeature#full_name}.'''
        result = self._values.get("full_name")
        assert result is not None, "Required property 'full_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringFeatureConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureFunction",
    jsii_struct_bases=[],
    name_mapping={
        "function_type": "functionType",
        "extra_parameters": "extraParameters",
    },
)
class DataDatabricksFeatureEngineeringFeatureFunction:
    def __init__(
        self,
        *,
        function_type: builtins.str,
        extra_parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#function_type DataDatabricksFeatureEngineeringFeature#function_type}.
        :param extra_parameters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#extra_parameters DataDatabricksFeatureEngineeringFeature#extra_parameters}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bc6eecdca15b788ad0db788de1ada487bddff1a72a2de960b308d557f857a97)
            check_type(argname="argument function_type", value=function_type, expected_type=type_hints["function_type"])
            check_type(argname="argument extra_parameters", value=extra_parameters, expected_type=type_hints["extra_parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "function_type": function_type,
        }
        if extra_parameters is not None:
            self._values["extra_parameters"] = extra_parameters

    @builtins.property
    def function_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#function_type DataDatabricksFeatureEngineeringFeature#function_type}.'''
        result = self._values.get("function_type")
        assert result is not None, "Required property 'function_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def extra_parameters(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#extra_parameters DataDatabricksFeatureEngineeringFeature#extra_parameters}.'''
        result = self._values.get("extra_parameters")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringFeatureFunction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#key DataDatabricksFeatureEngineeringFeature#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#value DataDatabricksFeatureEngineeringFeature#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9282289a5732341109e1f1902e01c17115e7f0504ef797cc9e0b5f6ed7744e8e)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#key DataDatabricksFeatureEngineeringFeature#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#value DataDatabricksFeatureEngineeringFeature#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a1ae1253371df7a089291818850e43844421e07456661c50c09a97378375f4c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f8bfaa24d532745199d92460b1661fe39f74b528187a2ce7db3d7b9549d6b66)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caf43c460e784501050985c1f6de736c564b33a405c6911d4443b59d35244ae0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43d8bcc35b15e643dc3ce51d920d6928c209aef6b82e35573b802793a7751f06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fb58a8dbcb8771ab7c1e410dac892c88083bda5ee5fa7aa4233c920588dc5dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__066ca5e281bfcd8e465e1b8f161127ccab32c59489d82c6957e300ff56d7c12e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cebb274864307f02c2e1156521db5cc7e125818e73a269696673c79f3fc353e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53b049d0c4e24838b77129ac56d5a28c441eddd8461990d1235fc7ab246be087)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d987847aa90f6b2ec34cfc697d83a1d64c302a38bdbd1f4c1da4d55d604e615)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28576b80d190f24d55fdc91891937451cd8d7a96aaef37d74acd91695d16300c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFeatureEngineeringFeatureFunctionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureFunctionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__37af949cdb92ed3873bf3801859cea3de4bd78f8205b3485bffa00bd7477ce43)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putExtraParameters")
    def put_extra_parameters(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f491cb6af1e2da6f4ce8ef7a954cbe7f5bdec072fb0ed4e0fdaad08cfef1c66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExtraParameters", [value]))

    @jsii.member(jsii_name="resetExtraParameters")
    def reset_extra_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtraParameters", []))

    @builtins.property
    @jsii.member(jsii_name="extraParameters")
    def extra_parameters(
        self,
    ) -> DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersList:
        return typing.cast(DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersList, jsii.get(self, "extraParameters"))

    @builtins.property
    @jsii.member(jsii_name="extraParametersInput")
    def extra_parameters_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]]], jsii.get(self, "extraParametersInput"))

    @builtins.property
    @jsii.member(jsii_name="functionTypeInput")
    def function_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="functionType")
    def function_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionType"))

    @function_type.setter
    def function_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__161495b2d3179831094cf01c5373e712ee1b03a49cbb00932591bcf25ca9646a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksFeatureEngineeringFeatureFunction]:
        return typing.cast(typing.Optional[DataDatabricksFeatureEngineeringFeatureFunction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksFeatureEngineeringFeatureFunction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f6402111dd505c781a5caaf3caa8dc0522711226edcb965a9fae7fc5bb44ba2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureSource",
    jsii_struct_bases=[],
    name_mapping={"delta_table_source": "deltaTableSource"},
)
class DataDatabricksFeatureEngineeringFeatureSource:
    def __init__(
        self,
        *,
        delta_table_source: typing.Optional[typing.Union["DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param delta_table_source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#delta_table_source DataDatabricksFeatureEngineeringFeature#delta_table_source}.
        '''
        if isinstance(delta_table_source, dict):
            delta_table_source = DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource(**delta_table_source)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f90cf4a6d69ce80441698abdd03231ae99c49e1a94fa12a4bf078f6c4a8e1c33)
            check_type(argname="argument delta_table_source", value=delta_table_source, expected_type=type_hints["delta_table_source"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if delta_table_source is not None:
            self._values["delta_table_source"] = delta_table_source

    @builtins.property
    def delta_table_source(
        self,
    ) -> typing.Optional["DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#delta_table_source DataDatabricksFeatureEngineeringFeature#delta_table_source}.'''
        result = self._values.get("delta_table_source")
        return typing.cast(typing.Optional["DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringFeatureSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource",
    jsii_struct_bases=[],
    name_mapping={
        "entity_columns": "entityColumns",
        "full_name": "fullName",
        "timeseries_column": "timeseriesColumn",
    },
)
class DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource:
    def __init__(
        self,
        *,
        entity_columns: typing.Sequence[builtins.str],
        full_name: builtins.str,
        timeseries_column: builtins.str,
    ) -> None:
        '''
        :param entity_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#entity_columns DataDatabricksFeatureEngineeringFeature#entity_columns}.
        :param full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#full_name DataDatabricksFeatureEngineeringFeature#full_name}.
        :param timeseries_column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#timeseries_column DataDatabricksFeatureEngineeringFeature#timeseries_column}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdd16209f2dd8b1845b029d9c2370384b3f0c5777c7891959c28c42612c65221)
            check_type(argname="argument entity_columns", value=entity_columns, expected_type=type_hints["entity_columns"])
            check_type(argname="argument full_name", value=full_name, expected_type=type_hints["full_name"])
            check_type(argname="argument timeseries_column", value=timeseries_column, expected_type=type_hints["timeseries_column"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "entity_columns": entity_columns,
            "full_name": full_name,
            "timeseries_column": timeseries_column,
        }

    @builtins.property
    def entity_columns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#entity_columns DataDatabricksFeatureEngineeringFeature#entity_columns}.'''
        result = self._values.get("entity_columns")
        assert result is not None, "Required property 'entity_columns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def full_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#full_name DataDatabricksFeatureEngineeringFeature#full_name}.'''
        result = self._values.get("full_name")
        assert result is not None, "Required property 'full_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeseries_column(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#timeseries_column DataDatabricksFeatureEngineeringFeature#timeseries_column}.'''
        result = self._values.get("timeseries_column")
        assert result is not None, "Required property 'timeseries_column' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__98e4bdace8cefcd0fa828d7b7879e7e10dfb9fd5958bd7d5617bce744bdc4e90)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="entityColumnsInput")
    def entity_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "entityColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="fullNameInput")
    def full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="timeseriesColumnInput")
    def timeseries_column_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeseriesColumnInput"))

    @builtins.property
    @jsii.member(jsii_name="entityColumns")
    def entity_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "entityColumns"))

    @entity_columns.setter
    def entity_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa0c9870805eb3490b5ec51f1dfd379cba486c3fcc50ce9700e449d7dda4cfe7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fullName")
    def full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullName"))

    @full_name.setter
    def full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bd11516a86c766072c9045e0993bfe0861134e2e6c9225f8617276a4c5efc9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeseriesColumn")
    def timeseries_column(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeseriesColumn"))

    @timeseries_column.setter
    def timeseries_column(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9216ee501bbdd4fa4847f716edfb367b8cf80e01849ffc4fbff71809a0763219)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeseriesColumn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43255264a4c28ac6a9d373d51554290777162d838d92067dbb9d0f3b3fa9c9f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFeatureEngineeringFeatureSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__877f960098fa85f31cdb6d403cb570a83f8f52ff6e46527a4afb98c7c4f257dd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDeltaTableSource")
    def put_delta_table_source(
        self,
        *,
        entity_columns: typing.Sequence[builtins.str],
        full_name: builtins.str,
        timeseries_column: builtins.str,
    ) -> None:
        '''
        :param entity_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#entity_columns DataDatabricksFeatureEngineeringFeature#entity_columns}.
        :param full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#full_name DataDatabricksFeatureEngineeringFeature#full_name}.
        :param timeseries_column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#timeseries_column DataDatabricksFeatureEngineeringFeature#timeseries_column}.
        '''
        value = DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource(
            entity_columns=entity_columns,
            full_name=full_name,
            timeseries_column=timeseries_column,
        )

        return typing.cast(None, jsii.invoke(self, "putDeltaTableSource", [value]))

    @jsii.member(jsii_name="resetDeltaTableSource")
    def reset_delta_table_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeltaTableSource", []))

    @builtins.property
    @jsii.member(jsii_name="deltaTableSource")
    def delta_table_source(
        self,
    ) -> DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSourceOutputReference:
        return typing.cast(DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSourceOutputReference, jsii.get(self, "deltaTableSource"))

    @builtins.property
    @jsii.member(jsii_name="deltaTableSourceInput")
    def delta_table_source_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource]], jsii.get(self, "deltaTableSourceInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksFeatureEngineeringFeatureSource]:
        return typing.cast(typing.Optional[DataDatabricksFeatureEngineeringFeatureSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksFeatureEngineeringFeatureSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4d4d86516a00aee4be9c99947c06eea64131d34968858ec00178428c2c7b9cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureTimeWindow",
    jsii_struct_bases=[],
    name_mapping={
        "continuous": "continuous",
        "sliding": "sliding",
        "tumbling": "tumbling",
    },
)
class DataDatabricksFeatureEngineeringFeatureTimeWindow:
    def __init__(
        self,
        *,
        continuous: typing.Optional[typing.Union["DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous", typing.Dict[builtins.str, typing.Any]]] = None,
        sliding: typing.Optional[typing.Union["DataDatabricksFeatureEngineeringFeatureTimeWindowSliding", typing.Dict[builtins.str, typing.Any]]] = None,
        tumbling: typing.Optional[typing.Union["DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param continuous: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#continuous DataDatabricksFeatureEngineeringFeature#continuous}.
        :param sliding: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#sliding DataDatabricksFeatureEngineeringFeature#sliding}.
        :param tumbling: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#tumbling DataDatabricksFeatureEngineeringFeature#tumbling}.
        '''
        if isinstance(continuous, dict):
            continuous = DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous(**continuous)
        if isinstance(sliding, dict):
            sliding = DataDatabricksFeatureEngineeringFeatureTimeWindowSliding(**sliding)
        if isinstance(tumbling, dict):
            tumbling = DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling(**tumbling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fe232d4dadbbcedb3221bcd6782acee1d8e89e6f1e60f3c2f9794adc509f4ec)
            check_type(argname="argument continuous", value=continuous, expected_type=type_hints["continuous"])
            check_type(argname="argument sliding", value=sliding, expected_type=type_hints["sliding"])
            check_type(argname="argument tumbling", value=tumbling, expected_type=type_hints["tumbling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if continuous is not None:
            self._values["continuous"] = continuous
        if sliding is not None:
            self._values["sliding"] = sliding
        if tumbling is not None:
            self._values["tumbling"] = tumbling

    @builtins.property
    def continuous(
        self,
    ) -> typing.Optional["DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#continuous DataDatabricksFeatureEngineeringFeature#continuous}.'''
        result = self._values.get("continuous")
        return typing.cast(typing.Optional["DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous"], result)

    @builtins.property
    def sliding(
        self,
    ) -> typing.Optional["DataDatabricksFeatureEngineeringFeatureTimeWindowSliding"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#sliding DataDatabricksFeatureEngineeringFeature#sliding}.'''
        result = self._values.get("sliding")
        return typing.cast(typing.Optional["DataDatabricksFeatureEngineeringFeatureTimeWindowSliding"], result)

    @builtins.property
    def tumbling(
        self,
    ) -> typing.Optional["DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#tumbling DataDatabricksFeatureEngineeringFeature#tumbling}.'''
        result = self._values.get("tumbling")
        return typing.cast(typing.Optional["DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringFeatureTimeWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous",
    jsii_struct_bases=[],
    name_mapping={"window_duration": "windowDuration", "offset": "offset"},
)
class DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous:
    def __init__(
        self,
        *,
        window_duration: builtins.str,
        offset: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param window_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#window_duration DataDatabricksFeatureEngineeringFeature#window_duration}.
        :param offset: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#offset DataDatabricksFeatureEngineeringFeature#offset}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__979255c174d2fac86fc8cd602a68d57aaab2d048103cf16e850024690f353ae9)
            check_type(argname="argument window_duration", value=window_duration, expected_type=type_hints["window_duration"])
            check_type(argname="argument offset", value=offset, expected_type=type_hints["offset"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "window_duration": window_duration,
        }
        if offset is not None:
            self._values["offset"] = offset

    @builtins.property
    def window_duration(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#window_duration DataDatabricksFeatureEngineeringFeature#window_duration}.'''
        result = self._values.get("window_duration")
        assert result is not None, "Required property 'window_duration' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def offset(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#offset DataDatabricksFeatureEngineeringFeature#offset}.'''
        result = self._values.get("offset")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFeatureEngineeringFeatureTimeWindowContinuousOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureTimeWindowContinuousOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__253f0c41adf037348d88eeff4e1629b2afb2c6b3c98b2195031bf722f52b455f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetOffset")
    def reset_offset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOffset", []))

    @builtins.property
    @jsii.member(jsii_name="offsetInput")
    def offset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "offsetInput"))

    @builtins.property
    @jsii.member(jsii_name="windowDurationInput")
    def window_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "windowDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="offset")
    def offset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "offset"))

    @offset.setter
    def offset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c4b4fefccb127d382c955cbdf501102e4dfd037cde4057bcd79fdfd0b7e8915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "offset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="windowDuration")
    def window_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "windowDuration"))

    @window_duration.setter
    def window_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__980689f9849c5284aff594720b9cc413ea6fd900eced4c7a4cf507fbed683717)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "windowDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcf14bf1507ea5d3c36de981efbfabee6338aa8fb08ad8b69c72347bd96bb8e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFeatureEngineeringFeatureTimeWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureTimeWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__912c1e3650226dd28b02651677aac837718fb0424089279da863cb255d42329e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putContinuous")
    def put_continuous(
        self,
        *,
        window_duration: builtins.str,
        offset: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param window_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#window_duration DataDatabricksFeatureEngineeringFeature#window_duration}.
        :param offset: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#offset DataDatabricksFeatureEngineeringFeature#offset}.
        '''
        value = DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous(
            window_duration=window_duration, offset=offset
        )

        return typing.cast(None, jsii.invoke(self, "putContinuous", [value]))

    @jsii.member(jsii_name="putSliding")
    def put_sliding(
        self,
        *,
        slide_duration: builtins.str,
        window_duration: builtins.str,
    ) -> None:
        '''
        :param slide_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#slide_duration DataDatabricksFeatureEngineeringFeature#slide_duration}.
        :param window_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#window_duration DataDatabricksFeatureEngineeringFeature#window_duration}.
        '''
        value = DataDatabricksFeatureEngineeringFeatureTimeWindowSliding(
            slide_duration=slide_duration, window_duration=window_duration
        )

        return typing.cast(None, jsii.invoke(self, "putSliding", [value]))

    @jsii.member(jsii_name="putTumbling")
    def put_tumbling(self, *, window_duration: builtins.str) -> None:
        '''
        :param window_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#window_duration DataDatabricksFeatureEngineeringFeature#window_duration}.
        '''
        value = DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling(
            window_duration=window_duration
        )

        return typing.cast(None, jsii.invoke(self, "putTumbling", [value]))

    @jsii.member(jsii_name="resetContinuous")
    def reset_continuous(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContinuous", []))

    @jsii.member(jsii_name="resetSliding")
    def reset_sliding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSliding", []))

    @jsii.member(jsii_name="resetTumbling")
    def reset_tumbling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTumbling", []))

    @builtins.property
    @jsii.member(jsii_name="continuous")
    def continuous(
        self,
    ) -> DataDatabricksFeatureEngineeringFeatureTimeWindowContinuousOutputReference:
        return typing.cast(DataDatabricksFeatureEngineeringFeatureTimeWindowContinuousOutputReference, jsii.get(self, "continuous"))

    @builtins.property
    @jsii.member(jsii_name="sliding")
    def sliding(
        self,
    ) -> "DataDatabricksFeatureEngineeringFeatureTimeWindowSlidingOutputReference":
        return typing.cast("DataDatabricksFeatureEngineeringFeatureTimeWindowSlidingOutputReference", jsii.get(self, "sliding"))

    @builtins.property
    @jsii.member(jsii_name="tumbling")
    def tumbling(
        self,
    ) -> "DataDatabricksFeatureEngineeringFeatureTimeWindowTumblingOutputReference":
        return typing.cast("DataDatabricksFeatureEngineeringFeatureTimeWindowTumblingOutputReference", jsii.get(self, "tumbling"))

    @builtins.property
    @jsii.member(jsii_name="continuousInput")
    def continuous_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous]], jsii.get(self, "continuousInput"))

    @builtins.property
    @jsii.member(jsii_name="slidingInput")
    def sliding_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFeatureEngineeringFeatureTimeWindowSliding"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFeatureEngineeringFeatureTimeWindowSliding"]], jsii.get(self, "slidingInput"))

    @builtins.property
    @jsii.member(jsii_name="tumblingInput")
    def tumbling_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling"]], jsii.get(self, "tumblingInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksFeatureEngineeringFeatureTimeWindow]:
        return typing.cast(typing.Optional[DataDatabricksFeatureEngineeringFeatureTimeWindow], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksFeatureEngineeringFeatureTimeWindow],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__130bcbbb06010a6747694d7571445a4475616373a3cb9fb38a24eb79496893e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureTimeWindowSliding",
    jsii_struct_bases=[],
    name_mapping={
        "slide_duration": "slideDuration",
        "window_duration": "windowDuration",
    },
)
class DataDatabricksFeatureEngineeringFeatureTimeWindowSliding:
    def __init__(
        self,
        *,
        slide_duration: builtins.str,
        window_duration: builtins.str,
    ) -> None:
        '''
        :param slide_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#slide_duration DataDatabricksFeatureEngineeringFeature#slide_duration}.
        :param window_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#window_duration DataDatabricksFeatureEngineeringFeature#window_duration}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1860c113fd772dfe129e7386e13d2306b9d6f5375581521a31a0e251a67dcec)
            check_type(argname="argument slide_duration", value=slide_duration, expected_type=type_hints["slide_duration"])
            check_type(argname="argument window_duration", value=window_duration, expected_type=type_hints["window_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "slide_duration": slide_duration,
            "window_duration": window_duration,
        }

    @builtins.property
    def slide_duration(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#slide_duration DataDatabricksFeatureEngineeringFeature#slide_duration}.'''
        result = self._values.get("slide_duration")
        assert result is not None, "Required property 'slide_duration' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def window_duration(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#window_duration DataDatabricksFeatureEngineeringFeature#window_duration}.'''
        result = self._values.get("window_duration")
        assert result is not None, "Required property 'window_duration' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringFeatureTimeWindowSliding(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFeatureEngineeringFeatureTimeWindowSlidingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureTimeWindowSlidingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__562df1518a1d8f467681fa981fdb81264b2ce7cf429f3f5c19433719b15180cc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="slideDurationInput")
    def slide_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "slideDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="windowDurationInput")
    def window_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "windowDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="slideDuration")
    def slide_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "slideDuration"))

    @slide_duration.setter
    def slide_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__077497b125a337329373923ce5f5f953759200ba5af65fb932fd4598ef2746cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slideDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="windowDuration")
    def window_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "windowDuration"))

    @window_duration.setter
    def window_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a74303525c413b0aa1a98e99b97eae65a437d851c5ded87d2125ac41dd220bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "windowDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowSliding]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowSliding]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowSliding]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9bd8cb8ad2243f654beaca044986fa4c9b020d4c05b6f033764c8e997f010d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling",
    jsii_struct_bases=[],
    name_mapping={"window_duration": "windowDuration"},
)
class DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling:
    def __init__(self, *, window_duration: builtins.str) -> None:
        '''
        :param window_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#window_duration DataDatabricksFeatureEngineeringFeature#window_duration}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cead6212a75a95cf6f41eff3dcdc6988c826a35fc74de61854124accc304b5de)
            check_type(argname="argument window_duration", value=window_duration, expected_type=type_hints["window_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "window_duration": window_duration,
        }

    @builtins.property
    def window_duration(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/feature_engineering_feature#window_duration DataDatabricksFeatureEngineeringFeature#window_duration}.'''
        result = self._values.get("window_duration")
        assert result is not None, "Required property 'window_duration' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFeatureEngineeringFeatureTimeWindowTumblingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFeatureEngineeringFeature.DataDatabricksFeatureEngineeringFeatureTimeWindowTumblingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9208df66c7a7e8bf19dc0967cb38ab055e1566f0ccd9e30486687d6ce608c95f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="windowDurationInput")
    def window_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "windowDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="windowDuration")
    def window_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "windowDuration"))

    @window_duration.setter
    def window_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14063d37f4c562008edebf5fe1d3cc30cc8eea8f63289c83cd3d32c34c55b013)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "windowDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28596a210cf932851af13116857ecac5ff5c32dfa521221e2fc37c92265ad035)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksFeatureEngineeringFeature",
    "DataDatabricksFeatureEngineeringFeatureConfig",
    "DataDatabricksFeatureEngineeringFeatureFunction",
    "DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters",
    "DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersList",
    "DataDatabricksFeatureEngineeringFeatureFunctionExtraParametersOutputReference",
    "DataDatabricksFeatureEngineeringFeatureFunctionOutputReference",
    "DataDatabricksFeatureEngineeringFeatureSource",
    "DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource",
    "DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSourceOutputReference",
    "DataDatabricksFeatureEngineeringFeatureSourceOutputReference",
    "DataDatabricksFeatureEngineeringFeatureTimeWindow",
    "DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous",
    "DataDatabricksFeatureEngineeringFeatureTimeWindowContinuousOutputReference",
    "DataDatabricksFeatureEngineeringFeatureTimeWindowOutputReference",
    "DataDatabricksFeatureEngineeringFeatureTimeWindowSliding",
    "DataDatabricksFeatureEngineeringFeatureTimeWindowSlidingOutputReference",
    "DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling",
    "DataDatabricksFeatureEngineeringFeatureTimeWindowTumblingOutputReference",
]

publication.publish()

def _typecheckingstub__a3696c21da7bde97eef80dcada822c535ddaab0edcbb1e4eb8d43380d1642286(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    full_name: builtins.str,
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

def _typecheckingstub__cf501f315949e3e858c2e5f0ec5b124e8c2e5d9cab0eb90a4e0b284644c4173d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7058d7db513a7dcdf5a801f30d0d0b26af9a4c8afe70fe403afe6e62a06914e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0997a45d89fb01f308fdec91b6ec0788a53aa1617788db94dbe19d24ff86b3d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    full_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bc6eecdca15b788ad0db788de1ada487bddff1a72a2de960b308d557f857a97(
    *,
    function_type: builtins.str,
    extra_parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9282289a5732341109e1f1902e01c17115e7f0504ef797cc9e0b5f6ed7744e8e(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a1ae1253371df7a089291818850e43844421e07456661c50c09a97378375f4c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f8bfaa24d532745199d92460b1661fe39f74b528187a2ce7db3d7b9549d6b66(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caf43c460e784501050985c1f6de736c564b33a405c6911d4443b59d35244ae0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43d8bcc35b15e643dc3ce51d920d6928c209aef6b82e35573b802793a7751f06(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fb58a8dbcb8771ab7c1e410dac892c88083bda5ee5fa7aa4233c920588dc5dd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__066ca5e281bfcd8e465e1b8f161127ccab32c59489d82c6957e300ff56d7c12e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cebb274864307f02c2e1156521db5cc7e125818e73a269696673c79f3fc353e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53b049d0c4e24838b77129ac56d5a28c441eddd8461990d1235fc7ab246be087(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d987847aa90f6b2ec34cfc697d83a1d64c302a38bdbd1f4c1da4d55d604e615(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28576b80d190f24d55fdc91891937451cd8d7a96aaef37d74acd91695d16300c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37af949cdb92ed3873bf3801859cea3de4bd78f8205b3485bffa00bd7477ce43(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f491cb6af1e2da6f4ce8ef7a954cbe7f5bdec072fb0ed4e0fdaad08cfef1c66(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFeatureEngineeringFeatureFunctionExtraParameters, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__161495b2d3179831094cf01c5373e712ee1b03a49cbb00932591bcf25ca9646a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f6402111dd505c781a5caaf3caa8dc0522711226edcb965a9fae7fc5bb44ba2(
    value: typing.Optional[DataDatabricksFeatureEngineeringFeatureFunction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f90cf4a6d69ce80441698abdd03231ae99c49e1a94fa12a4bf078f6c4a8e1c33(
    *,
    delta_table_source: typing.Optional[typing.Union[DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdd16209f2dd8b1845b029d9c2370384b3f0c5777c7891959c28c42612c65221(
    *,
    entity_columns: typing.Sequence[builtins.str],
    full_name: builtins.str,
    timeseries_column: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98e4bdace8cefcd0fa828d7b7879e7e10dfb9fd5958bd7d5617bce744bdc4e90(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa0c9870805eb3490b5ec51f1dfd379cba486c3fcc50ce9700e449d7dda4cfe7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bd11516a86c766072c9045e0993bfe0861134e2e6c9225f8617276a4c5efc9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9216ee501bbdd4fa4847f716edfb367b8cf80e01849ffc4fbff71809a0763219(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43255264a4c28ac6a9d373d51554290777162d838d92067dbb9d0f3b3fa9c9f7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureSourceDeltaTableSource]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__877f960098fa85f31cdb6d403cb570a83f8f52ff6e46527a4afb98c7c4f257dd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4d4d86516a00aee4be9c99947c06eea64131d34968858ec00178428c2c7b9cc(
    value: typing.Optional[DataDatabricksFeatureEngineeringFeatureSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fe232d4dadbbcedb3221bcd6782acee1d8e89e6f1e60f3c2f9794adc509f4ec(
    *,
    continuous: typing.Optional[typing.Union[DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous, typing.Dict[builtins.str, typing.Any]]] = None,
    sliding: typing.Optional[typing.Union[DataDatabricksFeatureEngineeringFeatureTimeWindowSliding, typing.Dict[builtins.str, typing.Any]]] = None,
    tumbling: typing.Optional[typing.Union[DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__979255c174d2fac86fc8cd602a68d57aaab2d048103cf16e850024690f353ae9(
    *,
    window_duration: builtins.str,
    offset: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__253f0c41adf037348d88eeff4e1629b2afb2c6b3c98b2195031bf722f52b455f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c4b4fefccb127d382c955cbdf501102e4dfd037cde4057bcd79fdfd0b7e8915(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__980689f9849c5284aff594720b9cc413ea6fd900eced4c7a4cf507fbed683717(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcf14bf1507ea5d3c36de981efbfabee6338aa8fb08ad8b69c72347bd96bb8e5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowContinuous]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__912c1e3650226dd28b02651677aac837718fb0424089279da863cb255d42329e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__130bcbbb06010a6747694d7571445a4475616373a3cb9fb38a24eb79496893e3(
    value: typing.Optional[DataDatabricksFeatureEngineeringFeatureTimeWindow],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1860c113fd772dfe129e7386e13d2306b9d6f5375581521a31a0e251a67dcec(
    *,
    slide_duration: builtins.str,
    window_duration: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__562df1518a1d8f467681fa981fdb81264b2ce7cf429f3f5c19433719b15180cc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__077497b125a337329373923ce5f5f953759200ba5af65fb932fd4598ef2746cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a74303525c413b0aa1a98e99b97eae65a437d851c5ded87d2125ac41dd220bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9bd8cb8ad2243f654beaca044986fa4c9b020d4c05b6f033764c8e997f010d1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowSliding]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cead6212a75a95cf6f41eff3dcdc6988c826a35fc74de61854124accc304b5de(
    *,
    window_duration: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9208df66c7a7e8bf19dc0967cb38ab055e1566f0ccd9e30486687d6ce608c95f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14063d37f4c562008edebf5fe1d3cc30cc8eea8f63289c83cd3d32c34c55b013(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28596a210cf932851af13116857ecac5ff5c32dfa521221e2fc37c92265ad035(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFeatureEngineeringFeatureTimeWindowTumbling]],
) -> None:
    """Type checking stubs"""
    pass
