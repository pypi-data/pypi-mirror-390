r'''
# `data_databricks_budget_policies`

Refer to the Terraform Registry for docs: [`data_databricks_budget_policies`](https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies).
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


class DataDatabricksBudgetPolicies(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPolicies",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies databricks_budget_policies}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        filter_by: typing.Optional[typing.Union["DataDatabricksBudgetPoliciesFilterBy", typing.Dict[builtins.str, typing.Any]]] = None,
        page_size: typing.Optional[jsii.Number] = None,
        sort_spec: typing.Optional[typing.Union["DataDatabricksBudgetPoliciesSortSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies databricks_budget_policies} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#filter_by DataDatabricksBudgetPolicies#filter_by}.
        :param page_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#page_size DataDatabricksBudgetPolicies#page_size}.
        :param sort_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#sort_spec DataDatabricksBudgetPolicies#sort_spec}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__308da16ebe59212b718d934ee0e554476963cda8437b126ae712fb69aa0098f4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksBudgetPoliciesConfig(
            filter_by=filter_by,
            page_size=page_size,
            sort_spec=sort_spec,
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
        '''Generates CDKTF code for importing a DataDatabricksBudgetPolicies resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksBudgetPolicies to import.
        :param import_from_id: The id of the existing DataDatabricksBudgetPolicies that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksBudgetPolicies to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10a3489902124f50cc9b08b5a351de39c98e08ea506ef50a30b5ea03bde0b936)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFilterBy")
    def put_filter_by(
        self,
        *,
        creator_user_id: typing.Optional[jsii.Number] = None,
        creator_user_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param creator_user_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#creator_user_id DataDatabricksBudgetPolicies#creator_user_id}.
        :param creator_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#creator_user_name DataDatabricksBudgetPolicies#creator_user_name}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#policy_name DataDatabricksBudgetPolicies#policy_name}.
        '''
        value = DataDatabricksBudgetPoliciesFilterBy(
            creator_user_id=creator_user_id,
            creator_user_name=creator_user_name,
            policy_name=policy_name,
        )

        return typing.cast(None, jsii.invoke(self, "putFilterBy", [value]))

    @jsii.member(jsii_name="putSortSpec")
    def put_sort_spec(
        self,
        *,
        descending: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        field: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param descending: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#descending DataDatabricksBudgetPolicies#descending}.
        :param field: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#field DataDatabricksBudgetPolicies#field}.
        '''
        value = DataDatabricksBudgetPoliciesSortSpec(
            descending=descending, field=field
        )

        return typing.cast(None, jsii.invoke(self, "putSortSpec", [value]))

    @jsii.member(jsii_name="resetFilterBy")
    def reset_filter_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilterBy", []))

    @jsii.member(jsii_name="resetPageSize")
    def reset_page_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPageSize", []))

    @jsii.member(jsii_name="resetSortSpec")
    def reset_sort_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSortSpec", []))

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
    @jsii.member(jsii_name="filterBy")
    def filter_by(self) -> "DataDatabricksBudgetPoliciesFilterByOutputReference":
        return typing.cast("DataDatabricksBudgetPoliciesFilterByOutputReference", jsii.get(self, "filterBy"))

    @builtins.property
    @jsii.member(jsii_name="policies")
    def policies(self) -> "DataDatabricksBudgetPoliciesPoliciesList":
        return typing.cast("DataDatabricksBudgetPoliciesPoliciesList", jsii.get(self, "policies"))

    @builtins.property
    @jsii.member(jsii_name="sortSpec")
    def sort_spec(self) -> "DataDatabricksBudgetPoliciesSortSpecOutputReference":
        return typing.cast("DataDatabricksBudgetPoliciesSortSpecOutputReference", jsii.get(self, "sortSpec"))

    @builtins.property
    @jsii.member(jsii_name="filterByInput")
    def filter_by_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksBudgetPoliciesFilterBy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksBudgetPoliciesFilterBy"]], jsii.get(self, "filterByInput"))

    @builtins.property
    @jsii.member(jsii_name="pageSizeInput")
    def page_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pageSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="sortSpecInput")
    def sort_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksBudgetPoliciesSortSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksBudgetPoliciesSortSpec"]], jsii.get(self, "sortSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="pageSize")
    def page_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pageSize"))

    @page_size.setter
    def page_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d1a160115a6f18ed6e306b629b11e4ec2c0fbb3b93f5979cab168cf7b01a76f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pageSize", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "filter_by": "filterBy",
        "page_size": "pageSize",
        "sort_spec": "sortSpec",
    },
)
class DataDatabricksBudgetPoliciesConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        filter_by: typing.Optional[typing.Union["DataDatabricksBudgetPoliciesFilterBy", typing.Dict[builtins.str, typing.Any]]] = None,
        page_size: typing.Optional[jsii.Number] = None,
        sort_spec: typing.Optional[typing.Union["DataDatabricksBudgetPoliciesSortSpec", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param filter_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#filter_by DataDatabricksBudgetPolicies#filter_by}.
        :param page_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#page_size DataDatabricksBudgetPolicies#page_size}.
        :param sort_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#sort_spec DataDatabricksBudgetPolicies#sort_spec}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter_by, dict):
            filter_by = DataDatabricksBudgetPoliciesFilterBy(**filter_by)
        if isinstance(sort_spec, dict):
            sort_spec = DataDatabricksBudgetPoliciesSortSpec(**sort_spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86427756d710f34c670ab4cacfd03541ec68d5fd6a5cfa4e7db19b280e1d0a10)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument filter_by", value=filter_by, expected_type=type_hints["filter_by"])
            check_type(argname="argument page_size", value=page_size, expected_type=type_hints["page_size"])
            check_type(argname="argument sort_spec", value=sort_spec, expected_type=type_hints["sort_spec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if filter_by is not None:
            self._values["filter_by"] = filter_by
        if page_size is not None:
            self._values["page_size"] = page_size
        if sort_spec is not None:
            self._values["sort_spec"] = sort_spec

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
    def filter_by(self) -> typing.Optional["DataDatabricksBudgetPoliciesFilterBy"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#filter_by DataDatabricksBudgetPolicies#filter_by}.'''
        result = self._values.get("filter_by")
        return typing.cast(typing.Optional["DataDatabricksBudgetPoliciesFilterBy"], result)

    @builtins.property
    def page_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#page_size DataDatabricksBudgetPolicies#page_size}.'''
        result = self._values.get("page_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sort_spec(self) -> typing.Optional["DataDatabricksBudgetPoliciesSortSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#sort_spec DataDatabricksBudgetPolicies#sort_spec}.'''
        result = self._values.get("sort_spec")
        return typing.cast(typing.Optional["DataDatabricksBudgetPoliciesSortSpec"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksBudgetPoliciesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesFilterBy",
    jsii_struct_bases=[],
    name_mapping={
        "creator_user_id": "creatorUserId",
        "creator_user_name": "creatorUserName",
        "policy_name": "policyName",
    },
)
class DataDatabricksBudgetPoliciesFilterBy:
    def __init__(
        self,
        *,
        creator_user_id: typing.Optional[jsii.Number] = None,
        creator_user_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param creator_user_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#creator_user_id DataDatabricksBudgetPolicies#creator_user_id}.
        :param creator_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#creator_user_name DataDatabricksBudgetPolicies#creator_user_name}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#policy_name DataDatabricksBudgetPolicies#policy_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f7e684db745d402441735befc824c486044f70e0548ab37f5f0b363efef91c2)
            check_type(argname="argument creator_user_id", value=creator_user_id, expected_type=type_hints["creator_user_id"])
            check_type(argname="argument creator_user_name", value=creator_user_name, expected_type=type_hints["creator_user_name"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if creator_user_id is not None:
            self._values["creator_user_id"] = creator_user_id
        if creator_user_name is not None:
            self._values["creator_user_name"] = creator_user_name
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def creator_user_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#creator_user_id DataDatabricksBudgetPolicies#creator_user_id}.'''
        result = self._values.get("creator_user_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def creator_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#creator_user_name DataDatabricksBudgetPolicies#creator_user_name}.'''
        result = self._values.get("creator_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#policy_name DataDatabricksBudgetPolicies#policy_name}.'''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksBudgetPoliciesFilterBy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksBudgetPoliciesFilterByOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesFilterByOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__999a18d93c2f95759e51ccb108b02625d978442273fdb8557fb2c373208e15e3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreatorUserId")
    def reset_creator_user_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatorUserId", []))

    @jsii.member(jsii_name="resetCreatorUserName")
    def reset_creator_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatorUserName", []))

    @jsii.member(jsii_name="resetPolicyName")
    def reset_policy_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyName", []))

    @builtins.property
    @jsii.member(jsii_name="creatorUserIdInput")
    def creator_user_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "creatorUserIdInput"))

    @builtins.property
    @jsii.member(jsii_name="creatorUserNameInput")
    def creator_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creatorUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="policyNameInput")
    def policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="creatorUserId")
    def creator_user_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creatorUserId"))

    @creator_user_id.setter
    def creator_user_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d84616c0dc10091ef624cf0a71990e349ec93d6ad48a208727412fc481727642)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creatorUserId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creatorUserName")
    def creator_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creatorUserName"))

    @creator_user_name.setter
    def creator_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e0a82559894fb25ce78d118507f5c17baf1444d6745fb99ae25497aee9f91d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creatorUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d454f49a9dc14d5b06502dd25f778a6b712e4a703985037620d3ced6387dba5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesFilterBy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesFilterBy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesFilterBy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__885718c0c1b18f094c95fc2c2668c70a5beaf30bc06bcc35a2a034678ff76924)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesPolicies",
    jsii_struct_bases=[],
    name_mapping={"policy_id": "policyId"},
)
class DataDatabricksBudgetPoliciesPolicies:
    def __init__(self, *, policy_id: builtins.str) -> None:
        '''
        :param policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#policy_id DataDatabricksBudgetPolicies#policy_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f0dd5d39fcabefdcb34d1ea3af9e8a0daf9c0689bdc26590766c0eeaf281685)
            check_type(argname="argument policy_id", value=policy_id, expected_type=type_hints["policy_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "policy_id": policy_id,
        }

    @builtins.property
    def policy_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#policy_id DataDatabricksBudgetPolicies#policy_id}.'''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksBudgetPoliciesPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesPoliciesCustomTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class DataDatabricksBudgetPoliciesPoliciesCustomTags:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#key DataDatabricksBudgetPolicies#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#value DataDatabricksBudgetPolicies#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab6f05051232af14a2c6e857416468718f4ef9f245d75af00fec14e243a8376b)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#key DataDatabricksBudgetPolicies#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#value DataDatabricksBudgetPolicies#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksBudgetPoliciesPoliciesCustomTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksBudgetPoliciesPoliciesCustomTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesPoliciesCustomTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bfdd36425ff71b392f6f9384e4b1807456b464684ca197794982111d8bb6af3a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksBudgetPoliciesPoliciesCustomTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2b0534c2a3831d9a38227640d7992e464d0380499e99aa628f084ecfe96b5bc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksBudgetPoliciesPoliciesCustomTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8018da4137ba39ffa2dfe2cd80c2fa6707118397bd202b592d27db3dad7fef88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f78964a8c2cf477df13726c5d35b711224953bb3c56184c7bb917598df52c9e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0547cc30dcab8950945c7fdbdf9d448213020fecc6f6a5f9e27409ff2bc0ca8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesPoliciesCustomTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesPoliciesCustomTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesPoliciesCustomTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb0f43a022372cd166f2678c1890f14adfe7db1d966bf023185649663a553988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksBudgetPoliciesPoliciesCustomTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesPoliciesCustomTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__432f8bf008808811270f8b4af448b878bb04dc0b80d5eba1a9dbdde8399aca81)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__27ecbfeb8ea4cbbaa9b5cb0b4eee00e64afce0776e1c8e6f982d36236bde9d90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f3a6fe42e3a217f1220f48ef0ba7f735998200a00e0eec3554641a16d9e0743)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksBudgetPoliciesPoliciesCustomTags]:
        return typing.cast(typing.Optional[DataDatabricksBudgetPoliciesPoliciesCustomTags], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksBudgetPoliciesPoliciesCustomTags],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__737841e043ac711ced36f8670c2b232095ac5fa4a3ea9b22133cdc35d76d7389)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksBudgetPoliciesPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesPoliciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7593c76628b638085c0adf78c027b3050fec0ebdfe382e64d061b8fb3d0e42e2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksBudgetPoliciesPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c54da1a65ff3a72875ca9dad1260329880cdaf75db6cdf5e5af660d09fc8233)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksBudgetPoliciesPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be6fd63bb80cfe6b39ca0650c9f573db0108b15cd082c936f23b0863e8f52174)
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
            type_hints = typing.get_type_hints(_typecheckingstub__302773c058e593549ca8b1db9a604396f1f9468a14d017037cd71a7917aad09b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3f560414d1383c5f4ce97b40dfad8b3ee03a597bcca39d837dcef4773fa4ad5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesPolicies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesPolicies]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesPolicies]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4506a1d0c533c4fc7c13ccac1522a902eb556b3b7c52bd8c74772e4bf5652ee9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksBudgetPoliciesPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesPoliciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__25b71de39ea649fc56a70f59a3e328e873d9870e918925d00cc84b89ae1cd2d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="bindingWorkspaceIds")
    def binding_workspace_ids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "bindingWorkspaceIds"))

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> DataDatabricksBudgetPoliciesPoliciesCustomTagsList:
        return typing.cast(DataDatabricksBudgetPoliciesPoliciesCustomTagsList, jsii.get(self, "customTags"))

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @builtins.property
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2338908496beb12a2fe62cf47a67c671c29021060c372ba00096049b8f08b7bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksBudgetPoliciesPolicies]:
        return typing.cast(typing.Optional[DataDatabricksBudgetPoliciesPolicies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksBudgetPoliciesPolicies],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38f344007b70f442ebe7aaefc03bb880fb9aa17e512bdc42fc61b7d85f79b616)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesSortSpec",
    jsii_struct_bases=[],
    name_mapping={"descending": "descending", "field": "field"},
)
class DataDatabricksBudgetPoliciesSortSpec:
    def __init__(
        self,
        *,
        descending: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        field: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param descending: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#descending DataDatabricksBudgetPolicies#descending}.
        :param field: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#field DataDatabricksBudgetPolicies#field}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f0159f9d644e62f92867c1354a41817d8f0cf0a38ea58c60c6bf6c5098601e8)
            check_type(argname="argument descending", value=descending, expected_type=type_hints["descending"])
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if descending is not None:
            self._values["descending"] = descending
        if field is not None:
            self._values["field"] = field

    @builtins.property
    def descending(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#descending DataDatabricksBudgetPolicies#descending}.'''
        result = self._values.get("descending")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def field(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.97.0/docs/data-sources/budget_policies#field DataDatabricksBudgetPolicies#field}.'''
        result = self._values.get("field")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksBudgetPoliciesSortSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksBudgetPoliciesSortSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesSortSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__713a78796e28f99b15c41ab2e8acf45637dee8ee8f9f030c69b9025f23e0e837)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDescending")
    def reset_descending(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescending", []))

    @jsii.member(jsii_name="resetField")
    def reset_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetField", []))

    @builtins.property
    @jsii.member(jsii_name="descendingInput")
    def descending_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "descendingInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldInput")
    def field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldInput"))

    @builtins.property
    @jsii.member(jsii_name="descending")
    def descending(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "descending"))

    @descending.setter
    def descending(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1535e128ada82de99b2b7d1fab1b173a838a8f9c963d4d27584cf48644a619fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "descending", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="field")
    def field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "field"))

    @field.setter
    def field(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eda49beaca87b3327b0a691e697eb9e1e54bd5108d245870c02d6840186d883)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "field", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesSortSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesSortSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesSortSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88a90db0e11f0130fbd0af91713c67d27214da2a20bd5b762cf5b817dfeb75a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksBudgetPolicies",
    "DataDatabricksBudgetPoliciesConfig",
    "DataDatabricksBudgetPoliciesFilterBy",
    "DataDatabricksBudgetPoliciesFilterByOutputReference",
    "DataDatabricksBudgetPoliciesPolicies",
    "DataDatabricksBudgetPoliciesPoliciesCustomTags",
    "DataDatabricksBudgetPoliciesPoliciesCustomTagsList",
    "DataDatabricksBudgetPoliciesPoliciesCustomTagsOutputReference",
    "DataDatabricksBudgetPoliciesPoliciesList",
    "DataDatabricksBudgetPoliciesPoliciesOutputReference",
    "DataDatabricksBudgetPoliciesSortSpec",
    "DataDatabricksBudgetPoliciesSortSpecOutputReference",
]

publication.publish()

def _typecheckingstub__308da16ebe59212b718d934ee0e554476963cda8437b126ae712fb69aa0098f4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    filter_by: typing.Optional[typing.Union[DataDatabricksBudgetPoliciesFilterBy, typing.Dict[builtins.str, typing.Any]]] = None,
    page_size: typing.Optional[jsii.Number] = None,
    sort_spec: typing.Optional[typing.Union[DataDatabricksBudgetPoliciesSortSpec, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__10a3489902124f50cc9b08b5a351de39c98e08ea506ef50a30b5ea03bde0b936(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d1a160115a6f18ed6e306b629b11e4ec2c0fbb3b93f5979cab168cf7b01a76f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86427756d710f34c670ab4cacfd03541ec68d5fd6a5cfa4e7db19b280e1d0a10(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    filter_by: typing.Optional[typing.Union[DataDatabricksBudgetPoliciesFilterBy, typing.Dict[builtins.str, typing.Any]]] = None,
    page_size: typing.Optional[jsii.Number] = None,
    sort_spec: typing.Optional[typing.Union[DataDatabricksBudgetPoliciesSortSpec, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f7e684db745d402441735befc824c486044f70e0548ab37f5f0b363efef91c2(
    *,
    creator_user_id: typing.Optional[jsii.Number] = None,
    creator_user_name: typing.Optional[builtins.str] = None,
    policy_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__999a18d93c2f95759e51ccb108b02625d978442273fdb8557fb2c373208e15e3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d84616c0dc10091ef624cf0a71990e349ec93d6ad48a208727412fc481727642(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e0a82559894fb25ce78d118507f5c17baf1444d6745fb99ae25497aee9f91d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d454f49a9dc14d5b06502dd25f778a6b712e4a703985037620d3ced6387dba5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__885718c0c1b18f094c95fc2c2668c70a5beaf30bc06bcc35a2a034678ff76924(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesFilterBy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f0dd5d39fcabefdcb34d1ea3af9e8a0daf9c0689bdc26590766c0eeaf281685(
    *,
    policy_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab6f05051232af14a2c6e857416468718f4ef9f245d75af00fec14e243a8376b(
    *,
    key: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfdd36425ff71b392f6f9384e4b1807456b464684ca197794982111d8bb6af3a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2b0534c2a3831d9a38227640d7992e464d0380499e99aa628f084ecfe96b5bc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8018da4137ba39ffa2dfe2cd80c2fa6707118397bd202b592d27db3dad7fef88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f78964a8c2cf477df13726c5d35b711224953bb3c56184c7bb917598df52c9e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0547cc30dcab8950945c7fdbdf9d448213020fecc6f6a5f9e27409ff2bc0ca8c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb0f43a022372cd166f2678c1890f14adfe7db1d966bf023185649663a553988(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesPoliciesCustomTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__432f8bf008808811270f8b4af448b878bb04dc0b80d5eba1a9dbdde8399aca81(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27ecbfeb8ea4cbbaa9b5cb0b4eee00e64afce0776e1c8e6f982d36236bde9d90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f3a6fe42e3a217f1220f48ef0ba7f735998200a00e0eec3554641a16d9e0743(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__737841e043ac711ced36f8670c2b232095ac5fa4a3ea9b22133cdc35d76d7389(
    value: typing.Optional[DataDatabricksBudgetPoliciesPoliciesCustomTags],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7593c76628b638085c0adf78c027b3050fec0ebdfe382e64d061b8fb3d0e42e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c54da1a65ff3a72875ca9dad1260329880cdaf75db6cdf5e5af660d09fc8233(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be6fd63bb80cfe6b39ca0650c9f573db0108b15cd082c936f23b0863e8f52174(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__302773c058e593549ca8b1db9a604396f1f9468a14d017037cd71a7917aad09b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3f560414d1383c5f4ce97b40dfad8b3ee03a597bcca39d837dcef4773fa4ad5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4506a1d0c533c4fc7c13ccac1522a902eb556b3b7c52bd8c74772e4bf5652ee9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesPolicies]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25b71de39ea649fc56a70f59a3e328e873d9870e918925d00cc84b89ae1cd2d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2338908496beb12a2fe62cf47a67c671c29021060c372ba00096049b8f08b7bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38f344007b70f442ebe7aaefc03bb880fb9aa17e512bdc42fc61b7d85f79b616(
    value: typing.Optional[DataDatabricksBudgetPoliciesPolicies],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f0159f9d644e62f92867c1354a41817d8f0cf0a38ea58c60c6bf6c5098601e8(
    *,
    descending: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    field: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__713a78796e28f99b15c41ab2e8acf45637dee8ee8f9f030c69b9025f23e0e837(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1535e128ada82de99b2b7d1fab1b173a838a8f9c963d4d27584cf48644a619fd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eda49beaca87b3327b0a691e697eb9e1e54bd5108d245870c02d6840186d883(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88a90db0e11f0130fbd0af91713c67d27214da2a20bd5b762cf5b817dfeb75a9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesSortSpec]],
) -> None:
    """Type checking stubs"""
    pass
