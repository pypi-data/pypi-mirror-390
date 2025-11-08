r'''
# `data_snowflake_authentication_policies`

Refer to the Terraform Registry for docs: [`data_snowflake_authentication_policies`](https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies).
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


class DataSnowflakeAuthenticationPolicies(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPolicies",
):
    '''Represents a {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies snowflake_authentication_policies}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        in_: typing.Optional[typing.Union["DataSnowflakeAuthenticationPoliciesIn", typing.Dict[builtins.str, typing.Any]]] = None,
        like: typing.Optional[builtins.str] = None,
        limit: typing.Optional[typing.Union["DataSnowflakeAuthenticationPoliciesLimit", typing.Dict[builtins.str, typing.Any]]] = None,
        on: typing.Optional[typing.Union["DataSnowflakeAuthenticationPoliciesOn", typing.Dict[builtins.str, typing.Any]]] = None,
        starts_with: typing.Optional[builtins.str] = None,
        with_describe: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies snowflake_authentication_policies} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#id DataSnowflakeAuthenticationPolicies#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param in_: in block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#in DataSnowflakeAuthenticationPolicies#in}
        :param like: Filters the output with **case-insensitive** pattern, with support for SQL wildcard characters (``%`` and ``_``). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#like DataSnowflakeAuthenticationPolicies#like}
        :param limit: limit block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#limit DataSnowflakeAuthenticationPolicies#limit}
        :param on: on block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#on DataSnowflakeAuthenticationPolicies#on}
        :param starts_with: Filters the output with **case-sensitive** characters indicating the beginning of the object name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#starts_with DataSnowflakeAuthenticationPolicies#starts_with}
        :param with_describe: (Default: ``true``) Runs DESC AUTHENTICATION POLICY for each service returned by SHOW AUTHENTICATION POLICIES. The output of describe is saved to the description field. By default this value is set to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#with_describe DataSnowflakeAuthenticationPolicies#with_describe}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c46e29fb687a58afec423aa48af95b0cdaf9ca319f2e530196fcf0e0ce122e6c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataSnowflakeAuthenticationPoliciesConfig(
            id=id,
            in_=in_,
            like=like,
            limit=limit,
            on=on,
            starts_with=starts_with,
            with_describe=with_describe,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DataSnowflakeAuthenticationPolicies resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataSnowflakeAuthenticationPolicies to import.
        :param import_from_id: The id of the existing DataSnowflakeAuthenticationPolicies that should be imported. Refer to the {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataSnowflakeAuthenticationPolicies to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c01c57033ec3ac90d9f9735f72136392c14bbe7dabead66a23cfb51c84951e1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putIn")
    def put_in(
        self,
        *,
        account: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        application: typing.Optional[builtins.str] = None,
        application_package: typing.Optional[builtins.str] = None,
        database: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: Returns records for the entire account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#account DataSnowflakeAuthenticationPolicies#account}
        :param application: Returns records for the specified application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#application DataSnowflakeAuthenticationPolicies#application}
        :param application_package: Returns records for the specified application package. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#application_package DataSnowflakeAuthenticationPolicies#application_package}
        :param database: Returns records for the current database in use or for a specified database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#database DataSnowflakeAuthenticationPolicies#database}
        :param schema: Returns records for the current schema in use or a specified schema. Use fully qualified name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#schema DataSnowflakeAuthenticationPolicies#schema}
        '''
        value = DataSnowflakeAuthenticationPoliciesIn(
            account=account,
            application=application,
            application_package=application_package,
            database=database,
            schema=schema,
        )

        return typing.cast(None, jsii.invoke(self, "putIn", [value]))

    @jsii.member(jsii_name="putLimit")
    def put_limit(
        self,
        *,
        rows: jsii.Number,
        from_: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param rows: The maximum number of rows to return. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#rows DataSnowflakeAuthenticationPolicies#rows}
        :param from_: Specifies a **case-sensitive** pattern that is used to match object name. After the first match, the limit on the number of rows will be applied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#from DataSnowflakeAuthenticationPolicies#from}
        '''
        value = DataSnowflakeAuthenticationPoliciesLimit(rows=rows, from_=from_)

        return typing.cast(None, jsii.invoke(self, "putLimit", [value]))

    @jsii.member(jsii_name="putOn")
    def put_on(
        self,
        *,
        account: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: Returns records for the entire account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#account DataSnowflakeAuthenticationPolicies#account}
        :param user: Returns records for the specified user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#user DataSnowflakeAuthenticationPolicies#user}
        '''
        value = DataSnowflakeAuthenticationPoliciesOn(account=account, user=user)

        return typing.cast(None, jsii.invoke(self, "putOn", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIn")
    def reset_in(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIn", []))

    @jsii.member(jsii_name="resetLike")
    def reset_like(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLike", []))

    @jsii.member(jsii_name="resetLimit")
    def reset_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLimit", []))

    @jsii.member(jsii_name="resetOn")
    def reset_on(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOn", []))

    @jsii.member(jsii_name="resetStartsWith")
    def reset_starts_with(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartsWith", []))

    @jsii.member(jsii_name="resetWithDescribe")
    def reset_with_describe(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWithDescribe", []))

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
    @jsii.member(jsii_name="authenticationPolicies")
    def authentication_policies(
        self,
    ) -> "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesList":
        return typing.cast("DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesList", jsii.get(self, "authenticationPolicies"))

    @builtins.property
    @jsii.member(jsii_name="in")
    def in_(self) -> "DataSnowflakeAuthenticationPoliciesInOutputReference":
        return typing.cast("DataSnowflakeAuthenticationPoliciesInOutputReference", jsii.get(self, "in"))

    @builtins.property
    @jsii.member(jsii_name="limit")
    def limit(self) -> "DataSnowflakeAuthenticationPoliciesLimitOutputReference":
        return typing.cast("DataSnowflakeAuthenticationPoliciesLimitOutputReference", jsii.get(self, "limit"))

    @builtins.property
    @jsii.member(jsii_name="on")
    def on(self) -> "DataSnowflakeAuthenticationPoliciesOnOutputReference":
        return typing.cast("DataSnowflakeAuthenticationPoliciesOnOutputReference", jsii.get(self, "on"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="inInput")
    def in_input(self) -> typing.Optional["DataSnowflakeAuthenticationPoliciesIn"]:
        return typing.cast(typing.Optional["DataSnowflakeAuthenticationPoliciesIn"], jsii.get(self, "inInput"))

    @builtins.property
    @jsii.member(jsii_name="likeInput")
    def like_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "likeInput"))

    @builtins.property
    @jsii.member(jsii_name="limitInput")
    def limit_input(
        self,
    ) -> typing.Optional["DataSnowflakeAuthenticationPoliciesLimit"]:
        return typing.cast(typing.Optional["DataSnowflakeAuthenticationPoliciesLimit"], jsii.get(self, "limitInput"))

    @builtins.property
    @jsii.member(jsii_name="onInput")
    def on_input(self) -> typing.Optional["DataSnowflakeAuthenticationPoliciesOn"]:
        return typing.cast(typing.Optional["DataSnowflakeAuthenticationPoliciesOn"], jsii.get(self, "onInput"))

    @builtins.property
    @jsii.member(jsii_name="startsWithInput")
    def starts_with_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startsWithInput"))

    @builtins.property
    @jsii.member(jsii_name="withDescribeInput")
    def with_describe_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "withDescribeInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eb000ef81643b472443dda66ea3ead6ea523aefcddfa0572b8913e06f698893)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="like")
    def like(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "like"))

    @like.setter
    def like(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17f73392b7cadbec863beef97639f96da9866a0897efb2f17ff271d2f2721953)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "like", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startsWith")
    def starts_with(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startsWith"))

    @starts_with.setter
    def starts_with(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__879cd5719dfca7583aa4d3acc3715dfea5289c55df187e28dd55f35806abe11b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startsWith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="withDescribe")
    def with_describe(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "withDescribe"))

    @with_describe.setter
    def with_describe(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c86b51ae3106f55883dbdc4f358b3f9f8f9f36f0d57ad8536d5ad44f26230bc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "withDescribe", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesAuthenticationPolicies",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataSnowflakeAuthenticationPoliciesAuthenticationPolicies:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSnowflakeAuthenticationPoliciesAuthenticationPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutput",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutput:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__646d893ee20133636c398f0639fd9c61f697587b2822d43b674276219559e348)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__800de80626fdd8503ef37ba16a496a8495e7f8ed8e4ae36d5c16a65d31c27237)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99196f02d7ed6a41c685d9045351068793482f4b95ab98e4ffbdf663133c72e1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__743481d8aaf3dda5dc6674da8470abd499f0bffab1817d79b8ee3226131f9f70)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8637b0ef7d7adbfd7734b30d2aa28afecd62fc10538ec51ca7dad7fecad3b57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf910788b2638d12b25a7baaa957f4d7053b484990fd1299b02f4d11063fc953)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="authenticationMethods")
    def authentication_methods(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationMethods"))

    @builtins.property
    @jsii.member(jsii_name="clientTypes")
    def client_types(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientTypes"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @builtins.property
    @jsii.member(jsii_name="mfaAuthenticationMethods")
    def mfa_authentication_methods(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mfaAuthenticationMethods"))

    @builtins.property
    @jsii.member(jsii_name="mfaEnrollment")
    def mfa_enrollment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mfaEnrollment"))

    @builtins.property
    @jsii.member(jsii_name="mfaPolicy")
    def mfa_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mfaPolicy"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property
    @jsii.member(jsii_name="patPolicy")
    def pat_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "patPolicy"))

    @builtins.property
    @jsii.member(jsii_name="securityIntegrations")
    def security_integrations(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityIntegrations"))

    @builtins.property
    @jsii.member(jsii_name="workloadIdentityPolicy")
    def workload_identity_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadIdentityPolicy"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutput]:
        return typing.cast(typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutput],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c8a8a09e374f5276e7a64a737c0ff925a7b5a7b46f80cabb4e2db295563cb52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__563a02eb7b721a71dbc918738cf9e1e8e518f14fb7b7ee99a7fbd74df93a1d99)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05a41a7233c5460e4cd5b70b3dbe9604befced58615f715918cb4e3a894ae9cb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b0e136178c310defebc1c45ed0ceda5d4532bbb9a04e7508253234a48481866)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d9b86a3f82ec339a8dcd9bc578010b8a4fd37303055ca4646c8bc4030e39852)
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
            type_hints = typing.get_type_hints(_typecheckingstub__60fcdbf34168880b6009de32543c66199aa701638b9728e618cfe533bed7192d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2139d27c032c046eeb1a2979042582bcad20bdad2c021fe92d25b6b6c38d4c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="describeOutput")
    def describe_output(
        self,
    ) -> DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputList:
        return typing.cast(DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputList, jsii.get(self, "describeOutput"))

    @builtins.property
    @jsii.member(jsii_name="showOutput")
    def show_output(
        self,
    ) -> "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputList":
        return typing.cast("DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputList", jsii.get(self, "showOutput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPolicies]:
        return typing.cast(typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPolicies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPolicies],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86ec0ffdef2a8bf1540f9ac478752818e642ef339ecf122a1ef5ec146043813d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutput",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutput:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b681f977fea7ae5abeeb68fad570dc32454cde04ece9ecd55b289bdd9446045a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__280cddfaba64356c849947f93c471153e1e960f8107181e8af10d9aa29ebf7ff)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dc82fa6317ec492e21faa0241566161bc826441a7b4d6624d2421b1b8cafb3a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__91ea2b9dc0aec12f3b883a31c9dc3d36c1023559bfc471077694deb42393d79a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec70445ca6fd64bd0b3f335b6a7e4a41ee0fac4b4f0b07efeb668a072ab0eeb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9221bc5aa4a76f23b0a5649c3d87e6f59d34222262e05593c0e102e5d06f67b7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @builtins.property
    @jsii.member(jsii_name="kind")
    def kind(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kind"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "options"))

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property
    @jsii.member(jsii_name="ownerRoleType")
    def owner_role_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerRoleType"))

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutput]:
        return typing.cast(typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutput],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7f462fadf5a61e5408fbd41423ea0920188b3dbe16f49858aa8cda5963dcb40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "id": "id",
        "in_": "in",
        "like": "like",
        "limit": "limit",
        "on": "on",
        "starts_with": "startsWith",
        "with_describe": "withDescribe",
    },
)
class DataSnowflakeAuthenticationPoliciesConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        in_: typing.Optional[typing.Union["DataSnowflakeAuthenticationPoliciesIn", typing.Dict[builtins.str, typing.Any]]] = None,
        like: typing.Optional[builtins.str] = None,
        limit: typing.Optional[typing.Union["DataSnowflakeAuthenticationPoliciesLimit", typing.Dict[builtins.str, typing.Any]]] = None,
        on: typing.Optional[typing.Union["DataSnowflakeAuthenticationPoliciesOn", typing.Dict[builtins.str, typing.Any]]] = None,
        starts_with: typing.Optional[builtins.str] = None,
        with_describe: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#id DataSnowflakeAuthenticationPolicies#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param in_: in block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#in DataSnowflakeAuthenticationPolicies#in}
        :param like: Filters the output with **case-insensitive** pattern, with support for SQL wildcard characters (``%`` and ``_``). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#like DataSnowflakeAuthenticationPolicies#like}
        :param limit: limit block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#limit DataSnowflakeAuthenticationPolicies#limit}
        :param on: on block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#on DataSnowflakeAuthenticationPolicies#on}
        :param starts_with: Filters the output with **case-sensitive** characters indicating the beginning of the object name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#starts_with DataSnowflakeAuthenticationPolicies#starts_with}
        :param with_describe: (Default: ``true``) Runs DESC AUTHENTICATION POLICY for each service returned by SHOW AUTHENTICATION POLICIES. The output of describe is saved to the description field. By default this value is set to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#with_describe DataSnowflakeAuthenticationPolicies#with_describe}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(in_, dict):
            in_ = DataSnowflakeAuthenticationPoliciesIn(**in_)
        if isinstance(limit, dict):
            limit = DataSnowflakeAuthenticationPoliciesLimit(**limit)
        if isinstance(on, dict):
            on = DataSnowflakeAuthenticationPoliciesOn(**on)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08b24c947f1a0695166ea907852b9454a1c2fb83b651eec746a28c96e36f7c8c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument in_", value=in_, expected_type=type_hints["in_"])
            check_type(argname="argument like", value=like, expected_type=type_hints["like"])
            check_type(argname="argument limit", value=limit, expected_type=type_hints["limit"])
            check_type(argname="argument on", value=on, expected_type=type_hints["on"])
            check_type(argname="argument starts_with", value=starts_with, expected_type=type_hints["starts_with"])
            check_type(argname="argument with_describe", value=with_describe, expected_type=type_hints["with_describe"])
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
        if id is not None:
            self._values["id"] = id
        if in_ is not None:
            self._values["in_"] = in_
        if like is not None:
            self._values["like"] = like
        if limit is not None:
            self._values["limit"] = limit
        if on is not None:
            self._values["on"] = on
        if starts_with is not None:
            self._values["starts_with"] = starts_with
        if with_describe is not None:
            self._values["with_describe"] = with_describe

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
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#id DataSnowflakeAuthenticationPolicies#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def in_(self) -> typing.Optional["DataSnowflakeAuthenticationPoliciesIn"]:
        '''in block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#in DataSnowflakeAuthenticationPolicies#in}
        '''
        result = self._values.get("in_")
        return typing.cast(typing.Optional["DataSnowflakeAuthenticationPoliciesIn"], result)

    @builtins.property
    def like(self) -> typing.Optional[builtins.str]:
        '''Filters the output with **case-insensitive** pattern, with support for SQL wildcard characters (``%`` and ``_``).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#like DataSnowflakeAuthenticationPolicies#like}
        '''
        result = self._values.get("like")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def limit(self) -> typing.Optional["DataSnowflakeAuthenticationPoliciesLimit"]:
        '''limit block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#limit DataSnowflakeAuthenticationPolicies#limit}
        '''
        result = self._values.get("limit")
        return typing.cast(typing.Optional["DataSnowflakeAuthenticationPoliciesLimit"], result)

    @builtins.property
    def on(self) -> typing.Optional["DataSnowflakeAuthenticationPoliciesOn"]:
        '''on block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#on DataSnowflakeAuthenticationPolicies#on}
        '''
        result = self._values.get("on")
        return typing.cast(typing.Optional["DataSnowflakeAuthenticationPoliciesOn"], result)

    @builtins.property
    def starts_with(self) -> typing.Optional[builtins.str]:
        '''Filters the output with **case-sensitive** characters indicating the beginning of the object name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#starts_with DataSnowflakeAuthenticationPolicies#starts_with}
        '''
        result = self._values.get("starts_with")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def with_describe(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''(Default: ``true``) Runs DESC AUTHENTICATION POLICY for each service returned by SHOW AUTHENTICATION POLICIES.

        The output of describe is saved to the description field. By default this value is set to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#with_describe DataSnowflakeAuthenticationPolicies#with_describe}
        '''
        result = self._values.get("with_describe")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSnowflakeAuthenticationPoliciesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesIn",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "application": "application",
        "application_package": "applicationPackage",
        "database": "database",
        "schema": "schema",
    },
)
class DataSnowflakeAuthenticationPoliciesIn:
    def __init__(
        self,
        *,
        account: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        application: typing.Optional[builtins.str] = None,
        application_package: typing.Optional[builtins.str] = None,
        database: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: Returns records for the entire account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#account DataSnowflakeAuthenticationPolicies#account}
        :param application: Returns records for the specified application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#application DataSnowflakeAuthenticationPolicies#application}
        :param application_package: Returns records for the specified application package. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#application_package DataSnowflakeAuthenticationPolicies#application_package}
        :param database: Returns records for the current database in use or for a specified database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#database DataSnowflakeAuthenticationPolicies#database}
        :param schema: Returns records for the current schema in use or a specified schema. Use fully qualified name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#schema DataSnowflakeAuthenticationPolicies#schema}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95977853d247f9e78445b7cf46ba13868a948ef12aee563493db4cbd10527e6a)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument application_package", value=application_package, expected_type=type_hints["application_package"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if application is not None:
            self._values["application"] = application
        if application_package is not None:
            self._values["application_package"] = application_package
        if database is not None:
            self._values["database"] = database
        if schema is not None:
            self._values["schema"] = schema

    @builtins.property
    def account(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Returns records for the entire account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#account DataSnowflakeAuthenticationPolicies#account}
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def application(self) -> typing.Optional[builtins.str]:
        '''Returns records for the specified application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#application DataSnowflakeAuthenticationPolicies#application}
        '''
        result = self._values.get("application")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_package(self) -> typing.Optional[builtins.str]:
        '''Returns records for the specified application package.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#application_package DataSnowflakeAuthenticationPolicies#application_package}
        '''
        result = self._values.get("application_package")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database(self) -> typing.Optional[builtins.str]:
        '''Returns records for the current database in use or for a specified database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#database DataSnowflakeAuthenticationPolicies#database}
        '''
        result = self._values.get("database")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''Returns records for the current schema in use or a specified schema. Use fully qualified name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#schema DataSnowflakeAuthenticationPolicies#schema}
        '''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSnowflakeAuthenticationPoliciesIn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataSnowflakeAuthenticationPoliciesInOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesInOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__79b50aeb73a44888f9d375594fe8a6e6d7e310fab87487e9740e983d5c0e1afd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAccount")
    def reset_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccount", []))

    @jsii.member(jsii_name="resetApplication")
    def reset_application(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplication", []))

    @jsii.member(jsii_name="resetApplicationPackage")
    def reset_application_package(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationPackage", []))

    @jsii.member(jsii_name="resetDatabase")
    def reset_database(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabase", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @builtins.property
    @jsii.member(jsii_name="accountInput")
    def account_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "accountInput"))

    @builtins.property
    @jsii.member(jsii_name="applicationInput")
    def application_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationInput"))

    @builtins.property
    @jsii.member(jsii_name="applicationPackageInput")
    def application_package_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationPackageInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaInput"))

    @builtins.property
    @jsii.member(jsii_name="account")
    def account(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "account"))

    @account.setter
    def account(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5a11c703aa148ef2b9de928704ec84f5afa69296ed45cd7f0974adde9298d65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "account", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "application"))

    @application.setter
    def application(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bf51ec41c48761096b1126a22b5dac0870020bad6c38f3324bcfa05c49528d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "application", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="applicationPackage")
    def application_package(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationPackage"))

    @application_package.setter
    def application_package(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed299494ac575fc7478c17e44138dc641596dfe671e21bb68b9847610520028c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationPackage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec30314079446f0e59ab291319279796ff20653e1d379e32efbe1d0a9d9548a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ffaf05331d020d3cb6fa82d9f2f85cc3caf80fc95cf4c1cb02c1cc622845827)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataSnowflakeAuthenticationPoliciesIn]:
        return typing.cast(typing.Optional[DataSnowflakeAuthenticationPoliciesIn], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataSnowflakeAuthenticationPoliciesIn],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4131de3f2d613ba62cada383af0a04cc7833d775d4bdf5e5a2b5939fbb16f80d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesLimit",
    jsii_struct_bases=[],
    name_mapping={"rows": "rows", "from_": "from"},
)
class DataSnowflakeAuthenticationPoliciesLimit:
    def __init__(
        self,
        *,
        rows: jsii.Number,
        from_: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param rows: The maximum number of rows to return. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#rows DataSnowflakeAuthenticationPolicies#rows}
        :param from_: Specifies a **case-sensitive** pattern that is used to match object name. After the first match, the limit on the number of rows will be applied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#from DataSnowflakeAuthenticationPolicies#from}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a765fc8c42fc0436e6b9efb0439aab0921e969a7e3084caed93d051801dffa6f)
            check_type(argname="argument rows", value=rows, expected_type=type_hints["rows"])
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "rows": rows,
        }
        if from_ is not None:
            self._values["from_"] = from_

    @builtins.property
    def rows(self) -> jsii.Number:
        '''The maximum number of rows to return.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#rows DataSnowflakeAuthenticationPolicies#rows}
        '''
        result = self._values.get("rows")
        assert result is not None, "Required property 'rows' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        '''Specifies a **case-sensitive** pattern that is used to match object name.

        After the first match, the limit on the number of rows will be applied.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#from DataSnowflakeAuthenticationPolicies#from}
        '''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSnowflakeAuthenticationPoliciesLimit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataSnowflakeAuthenticationPoliciesLimitOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesLimitOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a57f2228351a4b301d763f99383b406406f107d779638c94dd3812d5e865ee0d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFrom")
    def reset_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrom", []))

    @builtins.property
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromInput"))

    @builtins.property
    @jsii.member(jsii_name="rowsInput")
    def rows_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rowsInput"))

    @builtins.property
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b52a101b71b74a538c8ec0de5839c8e267007116e6365690c74ec97a53c45fcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rows")
    def rows(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rows"))

    @rows.setter
    def rows(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce219fe8a6a176e259958e952fa218e3b71c0a5b0cb5bce8526b68a7bd7fd16e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataSnowflakeAuthenticationPoliciesLimit]:
        return typing.cast(typing.Optional[DataSnowflakeAuthenticationPoliciesLimit], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataSnowflakeAuthenticationPoliciesLimit],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__255effc81378bb84f949b7b3c7aea63e7347fd380e62ce6f88517b8438bc29f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesOn",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "user": "user"},
)
class DataSnowflakeAuthenticationPoliciesOn:
    def __init__(
        self,
        *,
        account: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: Returns records for the entire account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#account DataSnowflakeAuthenticationPolicies#account}
        :param user: Returns records for the specified user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#user DataSnowflakeAuthenticationPolicies#user}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2afc6a515011d1e60e20556f2160f9def674fc52d9a727020dae78d68702e4b7)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument user", value=user, expected_type=type_hints["user"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if user is not None:
            self._values["user"] = user

    @builtins.property
    def account(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Returns records for the entire account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#account DataSnowflakeAuthenticationPolicies#account}
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''Returns records for the specified user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/data-sources/authentication_policies#user DataSnowflakeAuthenticationPolicies#user}
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSnowflakeAuthenticationPoliciesOn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataSnowflakeAuthenticationPoliciesOnOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.dataSnowflakeAuthenticationPolicies.DataSnowflakeAuthenticationPoliciesOnOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c3b6a74a308a9c33f6b54cefdb05f1532526e307cf89a733e8e01b151517edf8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAccount")
    def reset_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccount", []))

    @jsii.member(jsii_name="resetUser")
    def reset_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUser", []))

    @builtins.property
    @jsii.member(jsii_name="accountInput")
    def account_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "accountInput"))

    @builtins.property
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property
    @jsii.member(jsii_name="account")
    def account(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "account"))

    @account.setter
    def account(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1242dbe1614664f9a97ad10191ce4571cc02b6eeddaea1a333920b7a09216ef0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "account", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68bafc543896b59245683d51a98ed966e5babc4b573dc6950760268cc029b127)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataSnowflakeAuthenticationPoliciesOn]:
        return typing.cast(typing.Optional[DataSnowflakeAuthenticationPoliciesOn], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataSnowflakeAuthenticationPoliciesOn],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfe904e58c54f1336a69d3b4696fa55ccaaf4ad39be9581cb6da9972aa90e71b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataSnowflakeAuthenticationPolicies",
    "DataSnowflakeAuthenticationPoliciesAuthenticationPolicies",
    "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutput",
    "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputList",
    "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutputOutputReference",
    "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesList",
    "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesOutputReference",
    "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutput",
    "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputList",
    "DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutputOutputReference",
    "DataSnowflakeAuthenticationPoliciesConfig",
    "DataSnowflakeAuthenticationPoliciesIn",
    "DataSnowflakeAuthenticationPoliciesInOutputReference",
    "DataSnowflakeAuthenticationPoliciesLimit",
    "DataSnowflakeAuthenticationPoliciesLimitOutputReference",
    "DataSnowflakeAuthenticationPoliciesOn",
    "DataSnowflakeAuthenticationPoliciesOnOutputReference",
]

publication.publish()

def _typecheckingstub__c46e29fb687a58afec423aa48af95b0cdaf9ca319f2e530196fcf0e0ce122e6c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    id: typing.Optional[builtins.str] = None,
    in_: typing.Optional[typing.Union[DataSnowflakeAuthenticationPoliciesIn, typing.Dict[builtins.str, typing.Any]]] = None,
    like: typing.Optional[builtins.str] = None,
    limit: typing.Optional[typing.Union[DataSnowflakeAuthenticationPoliciesLimit, typing.Dict[builtins.str, typing.Any]]] = None,
    on: typing.Optional[typing.Union[DataSnowflakeAuthenticationPoliciesOn, typing.Dict[builtins.str, typing.Any]]] = None,
    starts_with: typing.Optional[builtins.str] = None,
    with_describe: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__4c01c57033ec3ac90d9f9735f72136392c14bbe7dabead66a23cfb51c84951e1(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eb000ef81643b472443dda66ea3ead6ea523aefcddfa0572b8913e06f698893(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17f73392b7cadbec863beef97639f96da9866a0897efb2f17ff271d2f2721953(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__879cd5719dfca7583aa4d3acc3715dfea5289c55df187e28dd55f35806abe11b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c86b51ae3106f55883dbdc4f358b3f9f8f9f36f0d57ad8536d5ad44f26230bc4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__646d893ee20133636c398f0639fd9c61f697587b2822d43b674276219559e348(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__800de80626fdd8503ef37ba16a496a8495e7f8ed8e4ae36d5c16a65d31c27237(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99196f02d7ed6a41c685d9045351068793482f4b95ab98e4ffbdf663133c72e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__743481d8aaf3dda5dc6674da8470abd499f0bffab1817d79b8ee3226131f9f70(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8637b0ef7d7adbfd7734b30d2aa28afecd62fc10538ec51ca7dad7fecad3b57(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf910788b2638d12b25a7baaa957f4d7053b484990fd1299b02f4d11063fc953(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c8a8a09e374f5276e7a64a737c0ff925a7b5a7b46f80cabb4e2db295563cb52(
    value: typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesDescribeOutput],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__563a02eb7b721a71dbc918738cf9e1e8e518f14fb7b7ee99a7fbd74df93a1d99(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05a41a7233c5460e4cd5b70b3dbe9604befced58615f715918cb4e3a894ae9cb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b0e136178c310defebc1c45ed0ceda5d4532bbb9a04e7508253234a48481866(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d9b86a3f82ec339a8dcd9bc578010b8a4fd37303055ca4646c8bc4030e39852(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60fcdbf34168880b6009de32543c66199aa701638b9728e618cfe533bed7192d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2139d27c032c046eeb1a2979042582bcad20bdad2c021fe92d25b6b6c38d4c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86ec0ffdef2a8bf1540f9ac478752818e642ef339ecf122a1ef5ec146043813d(
    value: typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPolicies],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b681f977fea7ae5abeeb68fad570dc32454cde04ece9ecd55b289bdd9446045a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__280cddfaba64356c849947f93c471153e1e960f8107181e8af10d9aa29ebf7ff(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dc82fa6317ec492e21faa0241566161bc826441a7b4d6624d2421b1b8cafb3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91ea2b9dc0aec12f3b883a31c9dc3d36c1023559bfc471077694deb42393d79a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec70445ca6fd64bd0b3f335b6a7e4a41ee0fac4b4f0b07efeb668a072ab0eeb7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9221bc5aa4a76f23b0a5649c3d87e6f59d34222262e05593c0e102e5d06f67b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7f462fadf5a61e5408fbd41423ea0920188b3dbe16f49858aa8cda5963dcb40(
    value: typing.Optional[DataSnowflakeAuthenticationPoliciesAuthenticationPoliciesShowOutput],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08b24c947f1a0695166ea907852b9454a1c2fb83b651eec746a28c96e36f7c8c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    in_: typing.Optional[typing.Union[DataSnowflakeAuthenticationPoliciesIn, typing.Dict[builtins.str, typing.Any]]] = None,
    like: typing.Optional[builtins.str] = None,
    limit: typing.Optional[typing.Union[DataSnowflakeAuthenticationPoliciesLimit, typing.Dict[builtins.str, typing.Any]]] = None,
    on: typing.Optional[typing.Union[DataSnowflakeAuthenticationPoliciesOn, typing.Dict[builtins.str, typing.Any]]] = None,
    starts_with: typing.Optional[builtins.str] = None,
    with_describe: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95977853d247f9e78445b7cf46ba13868a948ef12aee563493db4cbd10527e6a(
    *,
    account: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    application: typing.Optional[builtins.str] = None,
    application_package: typing.Optional[builtins.str] = None,
    database: typing.Optional[builtins.str] = None,
    schema: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79b50aeb73a44888f9d375594fe8a6e6d7e310fab87487e9740e983d5c0e1afd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5a11c703aa148ef2b9de928704ec84f5afa69296ed45cd7f0974adde9298d65(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bf51ec41c48761096b1126a22b5dac0870020bad6c38f3324bcfa05c49528d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed299494ac575fc7478c17e44138dc641596dfe671e21bb68b9847610520028c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec30314079446f0e59ab291319279796ff20653e1d379e32efbe1d0a9d9548a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ffaf05331d020d3cb6fa82d9f2f85cc3caf80fc95cf4c1cb02c1cc622845827(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4131de3f2d613ba62cada383af0a04cc7833d775d4bdf5e5a2b5939fbb16f80d(
    value: typing.Optional[DataSnowflakeAuthenticationPoliciesIn],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a765fc8c42fc0436e6b9efb0439aab0921e969a7e3084caed93d051801dffa6f(
    *,
    rows: jsii.Number,
    from_: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a57f2228351a4b301d763f99383b406406f107d779638c94dd3812d5e865ee0d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b52a101b71b74a538c8ec0de5839c8e267007116e6365690c74ec97a53c45fcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce219fe8a6a176e259958e952fa218e3b71c0a5b0cb5bce8526b68a7bd7fd16e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__255effc81378bb84f949b7b3c7aea63e7347fd380e62ce6f88517b8438bc29f1(
    value: typing.Optional[DataSnowflakeAuthenticationPoliciesLimit],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2afc6a515011d1e60e20556f2160f9def674fc52d9a727020dae78d68702e4b7(
    *,
    account: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    user: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3b6a74a308a9c33f6b54cefdb05f1532526e307cf89a733e8e01b151517edf8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1242dbe1614664f9a97ad10191ce4571cc02b6eeddaea1a333920b7a09216ef0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68bafc543896b59245683d51a98ed966e5babc4b573dc6950760268cc029b127(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfe904e58c54f1336a69d3b4696fa55ccaaf4ad39be9581cb6da9972aa90e71b(
    value: typing.Optional[DataSnowflakeAuthenticationPoliciesOn],
) -> None:
    """Type checking stubs"""
    pass
