r'''
# `snowflake_authentication_policy`

Refer to the Terraform Registry for docs: [`snowflake_authentication_policy`](https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy).
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


class AuthenticationPolicy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy snowflake_authentication_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        database: builtins.str,
        name: builtins.str,
        schema: builtins.str,
        authentication_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        client_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        comment: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        mfa_authentication_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        mfa_enrollment: typing.Optional[builtins.str] = None,
        mfa_policy: typing.Optional[typing.Union["AuthenticationPolicyMfaPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        pat_policy: typing.Optional[typing.Union["AuthenticationPolicyPatPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        security_integrations: typing.Optional[typing.Sequence[builtins.str]] = None,
        timeouts: typing.Optional[typing.Union["AuthenticationPolicyTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        workload_identity_policy: typing.Optional[typing.Union["AuthenticationPolicyWorkloadIdentityPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy snowflake_authentication_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param database: The database in which to create the authentication policy. Due to technical limitations (read more `here <../guides/identifiers_rework_design_decisions#known-limitations-and-identifier-recommendations>`_), avoid using the following characters: ``|``, ``.``, ``"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#database AuthenticationPolicy#database}
        :param name: Specifies the identifier for the authentication policy. Due to technical limitations (read more `here <../guides/identifiers_rework_design_decisions#known-limitations-and-identifier-recommendations>`_), avoid using the following characters: ``|``, ``.``, ``"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#name AuthenticationPolicy#name}
        :param schema: The schema in which to create the authentication policy. Due to technical limitations (read more `here <../guides/identifiers_rework_design_decisions#known-limitations-and-identifier-recommendations>`_), avoid using the following characters: ``|``, ``.``, ``"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#schema AuthenticationPolicy#schema}
        :param authentication_methods: A list of authentication methods that are allowed during login. Valid values are (case-insensitive): ``ALL`` | ``SAML`` | ``PASSWORD`` | ``OAUTH`` | ``KEYPAIR`` | ``PROGRAMMATIC_ACCESS_TOKEN`` | ``WORKLOAD_IDENTITY``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#authentication_methods AuthenticationPolicy#authentication_methods}
        :param client_types: A list of clients that can authenticate with Snowflake. If a client tries to connect, and the client is not one of the valid ``client_types``, then the login attempt fails. Valid values are (case-insensitive): ``ALL`` | ``SNOWFLAKE_UI`` | ``DRIVERS`` | ``SNOWSQL`` | ``SNOWFLAKE_CLI``. The ``client_types`` property of an authentication policy is a best effort method to block user logins based on specific clients. It should not be used as the sole control to establish a security boundary. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#client_types AuthenticationPolicy#client_types}
        :param comment: Specifies a comment for the authentication policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#comment AuthenticationPolicy#comment}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#id AuthenticationPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mfa_authentication_methods: A list of authentication methods that enforce multi-factor authentication (MFA) during login. Authentication methods not listed in this parameter do not prompt for multi-factor authentication. Allowed values are ``ALL`` | ``SAML`` | ``PASSWORD``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#mfa_authentication_methods AuthenticationPolicy#mfa_authentication_methods}
        :param mfa_enrollment: Determines whether a user must enroll in multi-factor authentication. Valid values are (case-insensitive): ``REQUIRED`` | ``REQUIRED_PASSWORD_ONLY`` | ``OPTIONAL``. When REQUIRED is specified, Enforces users to enroll in MFA. If this value is used, then the ``client_types`` parameter must include ``snowflake_ui``, because Snowsight is the only place users can enroll in multi-factor authentication (MFA). Note that when you set this value to OPTIONAL, and your account setup forces users to enroll in MFA, then Snowflake may set quietly this value to ``REQUIRED_PASSWORD_ONLY``, which may cause permadiff. In this case, you may want to adjust this field value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#mfa_enrollment AuthenticationPolicy#mfa_enrollment}
        :param mfa_policy: mfa_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#mfa_policy AuthenticationPolicy#mfa_policy}
        :param pat_policy: pat_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#pat_policy AuthenticationPolicy#pat_policy}
        :param security_integrations: A list of security integrations the authentication policy is associated with. This parameter has no effect when ``saml`` or ``oauth`` are not in the ``authentication_methods`` list. All values in the ``security_integrations`` list must be compatible with the values in the ``authentication_methods`` list. For example, if ``security_integrations`` contains a SAML security integration, and ``authentication_methods`` contains OAUTH, then you cannot create the authentication policy. To allow all security integrations use ``ALL`` as parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#security_integrations AuthenticationPolicy#security_integrations}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#timeouts AuthenticationPolicy#timeouts}
        :param workload_identity_policy: workload_identity_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#workload_identity_policy AuthenticationPolicy#workload_identity_policy}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77fb43a6a2493a8f92aa71cb59dc9a6e0cfce86f9a13283202805d7546a826ef)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AuthenticationPolicyConfig(
            database=database,
            name=name,
            schema=schema,
            authentication_methods=authentication_methods,
            client_types=client_types,
            comment=comment,
            id=id,
            mfa_authentication_methods=mfa_authentication_methods,
            mfa_enrollment=mfa_enrollment,
            mfa_policy=mfa_policy,
            pat_policy=pat_policy,
            security_integrations=security_integrations,
            timeouts=timeouts,
            workload_identity_policy=workload_identity_policy,
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
        '''Generates CDKTF code for importing a AuthenticationPolicy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AuthenticationPolicy to import.
        :param import_from_id: The id of the existing AuthenticationPolicy that should be imported. Refer to the {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AuthenticationPolicy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6196c97cfd956988d42d4f42ab1e2de4d23cfae668004274fbb54db2d87fb6c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putMfaPolicy")
    def put_mfa_policy(
        self,
        *,
        allowed_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        enforce_mfa_on_external_authentication: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_methods: Specifies the allowed methods for the MFA policy. Valid values are: ``ALL`` | ``PASSKEY`` | ``TOTP`` | ``DUO``. These values are case-sensitive due to Terraform limitations (it's a nested field). Prefer using uppercased values. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_methods AuthenticationPolicy#allowed_methods}
        :param enforce_mfa_on_external_authentication: Determines whether multi-factor authentication (MFA) is enforced on external authentication. Valid values are (case-insensitive): ``ALL`` | ``NONE``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#enforce_mfa_on_external_authentication AuthenticationPolicy#enforce_mfa_on_external_authentication}
        '''
        value = AuthenticationPolicyMfaPolicy(
            allowed_methods=allowed_methods,
            enforce_mfa_on_external_authentication=enforce_mfa_on_external_authentication,
        )

        return typing.cast(None, jsii.invoke(self, "putMfaPolicy", [value]))

    @jsii.member(jsii_name="putPatPolicy")
    def put_pat_policy(
        self,
        *,
        default_expiry_in_days: typing.Optional[jsii.Number] = None,
        max_expiry_in_days: typing.Optional[jsii.Number] = None,
        network_policy_evaluation: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_expiry_in_days: Specifies the default expiration time (in days) for a programmatic access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#default_expiry_in_days AuthenticationPolicy#default_expiry_in_days}
        :param max_expiry_in_days: Specifies the maximum number of days that can be set for the expiration time for a programmatic access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#max_expiry_in_days AuthenticationPolicy#max_expiry_in_days}
        :param network_policy_evaluation: Specifies the network policy evaluation for the PAT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#network_policy_evaluation AuthenticationPolicy#network_policy_evaluation}
        '''
        value = AuthenticationPolicyPatPolicy(
            default_expiry_in_days=default_expiry_in_days,
            max_expiry_in_days=max_expiry_in_days,
            network_policy_evaluation=network_policy_evaluation,
        )

        return typing.cast(None, jsii.invoke(self, "putPatPolicy", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#create AuthenticationPolicy#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#delete AuthenticationPolicy#delete}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#read AuthenticationPolicy#read}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#update AuthenticationPolicy#update}.
        '''
        value = AuthenticationPolicyTimeouts(
            create=create, delete=delete, read=read, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putWorkloadIdentityPolicy")
    def put_workload_identity_policy(
        self,
        *,
        allowed_aws_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_azure_issuers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_oidc_issuers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allowed_aws_accounts: Specifies the list of AWS account IDs allowed by the authentication policy during workload identity authentication of type ``AWS``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_aws_accounts AuthenticationPolicy#allowed_aws_accounts}
        :param allowed_azure_issuers: Specifies the list of Azure Entra ID issuers allowed by the authentication policy during workload identity authentication of type ``AZURE``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_azure_issuers AuthenticationPolicy#allowed_azure_issuers}
        :param allowed_oidc_issuers: Specifies the list of OIDC issuers allowed by the authentication policy during workload identity authentication of type ``OIDC``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_oidc_issuers AuthenticationPolicy#allowed_oidc_issuers}
        :param allowed_providers: Specifies the allowed providers for the workload identity policy. Valid values are: ``ALL`` | ``AWS`` | ``AZURE`` | ``GCP`` | ``OIDC``. These values are case-sensitive due to Terraform limitations (it's a nested field). Prefer using uppercased values. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_providers AuthenticationPolicy#allowed_providers}
        '''
        value = AuthenticationPolicyWorkloadIdentityPolicy(
            allowed_aws_accounts=allowed_aws_accounts,
            allowed_azure_issuers=allowed_azure_issuers,
            allowed_oidc_issuers=allowed_oidc_issuers,
            allowed_providers=allowed_providers,
        )

        return typing.cast(None, jsii.invoke(self, "putWorkloadIdentityPolicy", [value]))

    @jsii.member(jsii_name="resetAuthenticationMethods")
    def reset_authentication_methods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticationMethods", []))

    @jsii.member(jsii_name="resetClientTypes")
    def reset_client_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientTypes", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMfaAuthenticationMethods")
    def reset_mfa_authentication_methods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMfaAuthenticationMethods", []))

    @jsii.member(jsii_name="resetMfaEnrollment")
    def reset_mfa_enrollment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMfaEnrollment", []))

    @jsii.member(jsii_name="resetMfaPolicy")
    def reset_mfa_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMfaPolicy", []))

    @jsii.member(jsii_name="resetPatPolicy")
    def reset_pat_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPatPolicy", []))

    @jsii.member(jsii_name="resetSecurityIntegrations")
    def reset_security_integrations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityIntegrations", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetWorkloadIdentityPolicy")
    def reset_workload_identity_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadIdentityPolicy", []))

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
    @jsii.member(jsii_name="describeOutput")
    def describe_output(self) -> "AuthenticationPolicyDescribeOutputList":
        return typing.cast("AuthenticationPolicyDescribeOutputList", jsii.get(self, "describeOutput"))

    @builtins.property
    @jsii.member(jsii_name="fullyQualifiedName")
    def fully_qualified_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullyQualifiedName"))

    @builtins.property
    @jsii.member(jsii_name="mfaPolicy")
    def mfa_policy(self) -> "AuthenticationPolicyMfaPolicyOutputReference":
        return typing.cast("AuthenticationPolicyMfaPolicyOutputReference", jsii.get(self, "mfaPolicy"))

    @builtins.property
    @jsii.member(jsii_name="patPolicy")
    def pat_policy(self) -> "AuthenticationPolicyPatPolicyOutputReference":
        return typing.cast("AuthenticationPolicyPatPolicyOutputReference", jsii.get(self, "patPolicy"))

    @builtins.property
    @jsii.member(jsii_name="showOutput")
    def show_output(self) -> "AuthenticationPolicyShowOutputList":
        return typing.cast("AuthenticationPolicyShowOutputList", jsii.get(self, "showOutput"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "AuthenticationPolicyTimeoutsOutputReference":
        return typing.cast("AuthenticationPolicyTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="workloadIdentityPolicy")
    def workload_identity_policy(
        self,
    ) -> "AuthenticationPolicyWorkloadIdentityPolicyOutputReference":
        return typing.cast("AuthenticationPolicyWorkloadIdentityPolicyOutputReference", jsii.get(self, "workloadIdentityPolicy"))

    @builtins.property
    @jsii.member(jsii_name="authenticationMethodsInput")
    def authentication_methods_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "authenticationMethodsInput"))

    @builtins.property
    @jsii.member(jsii_name="clientTypesInput")
    def client_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "clientTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="mfaAuthenticationMethodsInput")
    def mfa_authentication_methods_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "mfaAuthenticationMethodsInput"))

    @builtins.property
    @jsii.member(jsii_name="mfaEnrollmentInput")
    def mfa_enrollment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mfaEnrollmentInput"))

    @builtins.property
    @jsii.member(jsii_name="mfaPolicyInput")
    def mfa_policy_input(self) -> typing.Optional["AuthenticationPolicyMfaPolicy"]:
        return typing.cast(typing.Optional["AuthenticationPolicyMfaPolicy"], jsii.get(self, "mfaPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="patPolicyInput")
    def pat_policy_input(self) -> typing.Optional["AuthenticationPolicyPatPolicy"]:
        return typing.cast(typing.Optional["AuthenticationPolicyPatPolicy"], jsii.get(self, "patPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaInput"))

    @builtins.property
    @jsii.member(jsii_name="securityIntegrationsInput")
    def security_integrations_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityIntegrationsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AuthenticationPolicyTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AuthenticationPolicyTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadIdentityPolicyInput")
    def workload_identity_policy_input(
        self,
    ) -> typing.Optional["AuthenticationPolicyWorkloadIdentityPolicy"]:
        return typing.cast(typing.Optional["AuthenticationPolicyWorkloadIdentityPolicy"], jsii.get(self, "workloadIdentityPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticationMethods")
    def authentication_methods(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "authenticationMethods"))

    @authentication_methods.setter
    def authentication_methods(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a211ec24767dd0d401bb98fa7d194b2221fa72c3133498be2aa0aecc7ab4bb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationMethods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientTypes")
    def client_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clientTypes"))

    @client_types.setter
    def client_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13b9316f3a70730e242f6ca2f064bc959681edff21bced6f8ce94fae70bec8cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec4bf234d4484ea595b7f5848c79ec1fd41c9fcee1d01647a75dd98d55069194)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dd1d000687e04454751c29eeeea8f9b64a027553d018d5cbf5bd954babe7bcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50a045c0a965a8550ad6bc387d3f70ed02261ae16cf2e880ecc38ecca3e73c0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mfaAuthenticationMethods")
    def mfa_authentication_methods(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mfaAuthenticationMethods"))

    @mfa_authentication_methods.setter
    def mfa_authentication_methods(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40c44db153fbfbdb186cafdfe5acf41c1000ddc3170b34294282fae10553dfed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mfaAuthenticationMethods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mfaEnrollment")
    def mfa_enrollment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mfaEnrollment"))

    @mfa_enrollment.setter
    def mfa_enrollment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__559ce969d56d5037f3cec06daa7f95057163249486b2d526e67bba524f42885f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mfaEnrollment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97bfe888ebb1a5e3d5f87558d866dd3ad6dc5e61c738d6478a2dd8c1680e12af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c10433f3a590b5ddf7af1c7bec2bf37665cce3716108abbade8ad02cc0317097)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityIntegrations")
    def security_integrations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityIntegrations"))

    @security_integrations.setter
    def security_integrations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__795a742bbc7bf6a7b5b005e6d8bc3ab8694dc7e6eb67b1904e6a9589f3a704ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityIntegrations", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "database": "database",
        "name": "name",
        "schema": "schema",
        "authentication_methods": "authenticationMethods",
        "client_types": "clientTypes",
        "comment": "comment",
        "id": "id",
        "mfa_authentication_methods": "mfaAuthenticationMethods",
        "mfa_enrollment": "mfaEnrollment",
        "mfa_policy": "mfaPolicy",
        "pat_policy": "patPolicy",
        "security_integrations": "securityIntegrations",
        "timeouts": "timeouts",
        "workload_identity_policy": "workloadIdentityPolicy",
    },
)
class AuthenticationPolicyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        database: builtins.str,
        name: builtins.str,
        schema: builtins.str,
        authentication_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        client_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        comment: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        mfa_authentication_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        mfa_enrollment: typing.Optional[builtins.str] = None,
        mfa_policy: typing.Optional[typing.Union["AuthenticationPolicyMfaPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        pat_policy: typing.Optional[typing.Union["AuthenticationPolicyPatPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        security_integrations: typing.Optional[typing.Sequence[builtins.str]] = None,
        timeouts: typing.Optional[typing.Union["AuthenticationPolicyTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        workload_identity_policy: typing.Optional[typing.Union["AuthenticationPolicyWorkloadIdentityPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param database: The database in which to create the authentication policy. Due to technical limitations (read more `here <../guides/identifiers_rework_design_decisions#known-limitations-and-identifier-recommendations>`_), avoid using the following characters: ``|``, ``.``, ``"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#database AuthenticationPolicy#database}
        :param name: Specifies the identifier for the authentication policy. Due to technical limitations (read more `here <../guides/identifiers_rework_design_decisions#known-limitations-and-identifier-recommendations>`_), avoid using the following characters: ``|``, ``.``, ``"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#name AuthenticationPolicy#name}
        :param schema: The schema in which to create the authentication policy. Due to technical limitations (read more `here <../guides/identifiers_rework_design_decisions#known-limitations-and-identifier-recommendations>`_), avoid using the following characters: ``|``, ``.``, ``"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#schema AuthenticationPolicy#schema}
        :param authentication_methods: A list of authentication methods that are allowed during login. Valid values are (case-insensitive): ``ALL`` | ``SAML`` | ``PASSWORD`` | ``OAUTH`` | ``KEYPAIR`` | ``PROGRAMMATIC_ACCESS_TOKEN`` | ``WORKLOAD_IDENTITY``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#authentication_methods AuthenticationPolicy#authentication_methods}
        :param client_types: A list of clients that can authenticate with Snowflake. If a client tries to connect, and the client is not one of the valid ``client_types``, then the login attempt fails. Valid values are (case-insensitive): ``ALL`` | ``SNOWFLAKE_UI`` | ``DRIVERS`` | ``SNOWSQL`` | ``SNOWFLAKE_CLI``. The ``client_types`` property of an authentication policy is a best effort method to block user logins based on specific clients. It should not be used as the sole control to establish a security boundary. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#client_types AuthenticationPolicy#client_types}
        :param comment: Specifies a comment for the authentication policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#comment AuthenticationPolicy#comment}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#id AuthenticationPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mfa_authentication_methods: A list of authentication methods that enforce multi-factor authentication (MFA) during login. Authentication methods not listed in this parameter do not prompt for multi-factor authentication. Allowed values are ``ALL`` | ``SAML`` | ``PASSWORD``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#mfa_authentication_methods AuthenticationPolicy#mfa_authentication_methods}
        :param mfa_enrollment: Determines whether a user must enroll in multi-factor authentication. Valid values are (case-insensitive): ``REQUIRED`` | ``REQUIRED_PASSWORD_ONLY`` | ``OPTIONAL``. When REQUIRED is specified, Enforces users to enroll in MFA. If this value is used, then the ``client_types`` parameter must include ``snowflake_ui``, because Snowsight is the only place users can enroll in multi-factor authentication (MFA). Note that when you set this value to OPTIONAL, and your account setup forces users to enroll in MFA, then Snowflake may set quietly this value to ``REQUIRED_PASSWORD_ONLY``, which may cause permadiff. In this case, you may want to adjust this field value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#mfa_enrollment AuthenticationPolicy#mfa_enrollment}
        :param mfa_policy: mfa_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#mfa_policy AuthenticationPolicy#mfa_policy}
        :param pat_policy: pat_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#pat_policy AuthenticationPolicy#pat_policy}
        :param security_integrations: A list of security integrations the authentication policy is associated with. This parameter has no effect when ``saml`` or ``oauth`` are not in the ``authentication_methods`` list. All values in the ``security_integrations`` list must be compatible with the values in the ``authentication_methods`` list. For example, if ``security_integrations`` contains a SAML security integration, and ``authentication_methods`` contains OAUTH, then you cannot create the authentication policy. To allow all security integrations use ``ALL`` as parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#security_integrations AuthenticationPolicy#security_integrations}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#timeouts AuthenticationPolicy#timeouts}
        :param workload_identity_policy: workload_identity_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#workload_identity_policy AuthenticationPolicy#workload_identity_policy}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(mfa_policy, dict):
            mfa_policy = AuthenticationPolicyMfaPolicy(**mfa_policy)
        if isinstance(pat_policy, dict):
            pat_policy = AuthenticationPolicyPatPolicy(**pat_policy)
        if isinstance(timeouts, dict):
            timeouts = AuthenticationPolicyTimeouts(**timeouts)
        if isinstance(workload_identity_policy, dict):
            workload_identity_policy = AuthenticationPolicyWorkloadIdentityPolicy(**workload_identity_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a119c304710bb6ee35cd6eec8be3372b24fec526b4232b6e5b6716f46a4dc15d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument authentication_methods", value=authentication_methods, expected_type=type_hints["authentication_methods"])
            check_type(argname="argument client_types", value=client_types, expected_type=type_hints["client_types"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument mfa_authentication_methods", value=mfa_authentication_methods, expected_type=type_hints["mfa_authentication_methods"])
            check_type(argname="argument mfa_enrollment", value=mfa_enrollment, expected_type=type_hints["mfa_enrollment"])
            check_type(argname="argument mfa_policy", value=mfa_policy, expected_type=type_hints["mfa_policy"])
            check_type(argname="argument pat_policy", value=pat_policy, expected_type=type_hints["pat_policy"])
            check_type(argname="argument security_integrations", value=security_integrations, expected_type=type_hints["security_integrations"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument workload_identity_policy", value=workload_identity_policy, expected_type=type_hints["workload_identity_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database": database,
            "name": name,
            "schema": schema,
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
        if authentication_methods is not None:
            self._values["authentication_methods"] = authentication_methods
        if client_types is not None:
            self._values["client_types"] = client_types
        if comment is not None:
            self._values["comment"] = comment
        if id is not None:
            self._values["id"] = id
        if mfa_authentication_methods is not None:
            self._values["mfa_authentication_methods"] = mfa_authentication_methods
        if mfa_enrollment is not None:
            self._values["mfa_enrollment"] = mfa_enrollment
        if mfa_policy is not None:
            self._values["mfa_policy"] = mfa_policy
        if pat_policy is not None:
            self._values["pat_policy"] = pat_policy
        if security_integrations is not None:
            self._values["security_integrations"] = security_integrations
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if workload_identity_policy is not None:
            self._values["workload_identity_policy"] = workload_identity_policy

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
    def database(self) -> builtins.str:
        '''The database in which to create the authentication policy.

        Due to technical limitations (read more `here <../guides/identifiers_rework_design_decisions#known-limitations-and-identifier-recommendations>`_), avoid using the following characters: ``|``, ``.``, ``"``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#database AuthenticationPolicy#database}
        '''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Specifies the identifier for the authentication policy.

        Due to technical limitations (read more `here <../guides/identifiers_rework_design_decisions#known-limitations-and-identifier-recommendations>`_), avoid using the following characters: ``|``, ``.``, ``"``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#name AuthenticationPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schema(self) -> builtins.str:
        '''The schema in which to create the authentication policy.

        Due to technical limitations (read more `here <../guides/identifiers_rework_design_decisions#known-limitations-and-identifier-recommendations>`_), avoid using the following characters: ``|``, ``.``, ``"``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#schema AuthenticationPolicy#schema}
        '''
        result = self._values.get("schema")
        assert result is not None, "Required property 'schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authentication_methods(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of authentication methods that are allowed during login.

        Valid values are (case-insensitive): ``ALL`` | ``SAML`` | ``PASSWORD`` | ``OAUTH`` | ``KEYPAIR`` | ``PROGRAMMATIC_ACCESS_TOKEN`` | ``WORKLOAD_IDENTITY``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#authentication_methods AuthenticationPolicy#authentication_methods}
        '''
        result = self._values.get("authentication_methods")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def client_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of clients that can authenticate with Snowflake.

        If a client tries to connect, and the client is not one of the valid ``client_types``, then the login attempt fails. Valid values are (case-insensitive): ``ALL`` | ``SNOWFLAKE_UI`` | ``DRIVERS`` | ``SNOWSQL`` | ``SNOWFLAKE_CLI``. The ``client_types`` property of an authentication policy is a best effort method to block user logins based on specific clients. It should not be used as the sole control to establish a security boundary.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#client_types AuthenticationPolicy#client_types}
        '''
        result = self._values.get("client_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Specifies a comment for the authentication policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#comment AuthenticationPolicy#comment}
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#id AuthenticationPolicy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mfa_authentication_methods(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of authentication methods that enforce multi-factor authentication (MFA) during login.

        Authentication methods not listed in this parameter do not prompt for multi-factor authentication. Allowed values are ``ALL`` | ``SAML`` | ``PASSWORD``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#mfa_authentication_methods AuthenticationPolicy#mfa_authentication_methods}
        '''
        result = self._values.get("mfa_authentication_methods")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def mfa_enrollment(self) -> typing.Optional[builtins.str]:
        '''Determines whether a user must enroll in multi-factor authentication.

        Valid values are (case-insensitive): ``REQUIRED`` | ``REQUIRED_PASSWORD_ONLY`` | ``OPTIONAL``. When REQUIRED is specified, Enforces users to enroll in MFA. If this value is used, then the ``client_types`` parameter must include ``snowflake_ui``, because Snowsight is the only place users can enroll in multi-factor authentication (MFA). Note that when you set this value to OPTIONAL, and your account setup forces users to enroll in MFA, then Snowflake may set quietly this value to ``REQUIRED_PASSWORD_ONLY``, which may cause permadiff. In this case, you may want to adjust this field value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#mfa_enrollment AuthenticationPolicy#mfa_enrollment}
        '''
        result = self._values.get("mfa_enrollment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mfa_policy(self) -> typing.Optional["AuthenticationPolicyMfaPolicy"]:
        '''mfa_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#mfa_policy AuthenticationPolicy#mfa_policy}
        '''
        result = self._values.get("mfa_policy")
        return typing.cast(typing.Optional["AuthenticationPolicyMfaPolicy"], result)

    @builtins.property
    def pat_policy(self) -> typing.Optional["AuthenticationPolicyPatPolicy"]:
        '''pat_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#pat_policy AuthenticationPolicy#pat_policy}
        '''
        result = self._values.get("pat_policy")
        return typing.cast(typing.Optional["AuthenticationPolicyPatPolicy"], result)

    @builtins.property
    def security_integrations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of security integrations the authentication policy is associated with.

        This parameter has no effect when ``saml`` or ``oauth`` are not in the ``authentication_methods`` list. All values in the ``security_integrations`` list must be compatible with the values in the ``authentication_methods`` list. For example, if ``security_integrations`` contains a SAML security integration, and ``authentication_methods`` contains OAUTH, then you cannot create the authentication policy. To allow all security integrations use ``ALL`` as parameter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#security_integrations AuthenticationPolicy#security_integrations}
        '''
        result = self._values.get("security_integrations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["AuthenticationPolicyTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#timeouts AuthenticationPolicy#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["AuthenticationPolicyTimeouts"], result)

    @builtins.property
    def workload_identity_policy(
        self,
    ) -> typing.Optional["AuthenticationPolicyWorkloadIdentityPolicy"]:
        '''workload_identity_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#workload_identity_policy AuthenticationPolicy#workload_identity_policy}
        '''
        result = self._values.get("workload_identity_policy")
        return typing.cast(typing.Optional["AuthenticationPolicyWorkloadIdentityPolicy"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthenticationPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyDescribeOutput",
    jsii_struct_bases=[],
    name_mapping={},
)
class AuthenticationPolicyDescribeOutput:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthenticationPolicyDescribeOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthenticationPolicyDescribeOutputList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyDescribeOutputList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__020e99a3ea32e58034c052cc3a12e7f37bfb82fe1dd8b78d5812d66d28d4bfae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AuthenticationPolicyDescribeOutputOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34d34877a162e0680b21cbd6384aa0323213d364dde4ae03ec6358550f32d313)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AuthenticationPolicyDescribeOutputOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af05419ad3dbf8bbc1fedccf5e0722076c7ad7bca4294173a8c4ce70214e884f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ddec069b41852a09df25f3526d1e3e047b3753485d3f5244a71646eee29d7ff)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c42a2133ea2c219e22efc2d6c52741a4c1814c378a933b46219a597c04e2704)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class AuthenticationPolicyDescribeOutputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyDescribeOutputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fc33d50d2c4660072d3f40595c2478b92e662b97fbe3799fd036988fee175b7)
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
    def internal_value(self) -> typing.Optional[AuthenticationPolicyDescribeOutput]:
        return typing.cast(typing.Optional[AuthenticationPolicyDescribeOutput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AuthenticationPolicyDescribeOutput],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08a72904a1a894519b701d3202d951b1fe6fecd88de7d1f65edf91247b78283d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyMfaPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_methods": "allowedMethods",
        "enforce_mfa_on_external_authentication": "enforceMfaOnExternalAuthentication",
    },
)
class AuthenticationPolicyMfaPolicy:
    def __init__(
        self,
        *,
        allowed_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        enforce_mfa_on_external_authentication: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_methods: Specifies the allowed methods for the MFA policy. Valid values are: ``ALL`` | ``PASSKEY`` | ``TOTP`` | ``DUO``. These values are case-sensitive due to Terraform limitations (it's a nested field). Prefer using uppercased values. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_methods AuthenticationPolicy#allowed_methods}
        :param enforce_mfa_on_external_authentication: Determines whether multi-factor authentication (MFA) is enforced on external authentication. Valid values are (case-insensitive): ``ALL`` | ``NONE``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#enforce_mfa_on_external_authentication AuthenticationPolicy#enforce_mfa_on_external_authentication}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abcecfc354f2e4198a8936aa1ec3fbb23344f64890354d3181c0113fbae9e731)
            check_type(argname="argument allowed_methods", value=allowed_methods, expected_type=type_hints["allowed_methods"])
            check_type(argname="argument enforce_mfa_on_external_authentication", value=enforce_mfa_on_external_authentication, expected_type=type_hints["enforce_mfa_on_external_authentication"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_methods is not None:
            self._values["allowed_methods"] = allowed_methods
        if enforce_mfa_on_external_authentication is not None:
            self._values["enforce_mfa_on_external_authentication"] = enforce_mfa_on_external_authentication

    @builtins.property
    def allowed_methods(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the allowed methods for the MFA policy.

        Valid values are: ``ALL`` | ``PASSKEY`` | ``TOTP`` | ``DUO``. These values are case-sensitive due to Terraform limitations (it's a nested field). Prefer using uppercased values.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_methods AuthenticationPolicy#allowed_methods}
        '''
        result = self._values.get("allowed_methods")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enforce_mfa_on_external_authentication(self) -> typing.Optional[builtins.str]:
        '''Determines whether multi-factor authentication (MFA) is enforced on external authentication. Valid values are (case-insensitive): ``ALL`` | ``NONE``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#enforce_mfa_on_external_authentication AuthenticationPolicy#enforce_mfa_on_external_authentication}
        '''
        result = self._values.get("enforce_mfa_on_external_authentication")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthenticationPolicyMfaPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthenticationPolicyMfaPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyMfaPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a7d0adf7a0640a9f07cba0c88757c5f2e26b2f30b0bfab3c6c32933cc9d3255)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowedMethods")
    def reset_allowed_methods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedMethods", []))

    @jsii.member(jsii_name="resetEnforceMfaOnExternalAuthentication")
    def reset_enforce_mfa_on_external_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceMfaOnExternalAuthentication", []))

    @builtins.property
    @jsii.member(jsii_name="allowedMethodsInput")
    def allowed_methods_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedMethodsInput"))

    @builtins.property
    @jsii.member(jsii_name="enforceMfaOnExternalAuthenticationInput")
    def enforce_mfa_on_external_authentication_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enforceMfaOnExternalAuthenticationInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedMethods")
    def allowed_methods(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedMethods"))

    @allowed_methods.setter
    def allowed_methods(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__180afcbd0b1f037e084e3b71f60fae2369f14a52856af80bbcb9c058b434fd95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedMethods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enforceMfaOnExternalAuthentication")
    def enforce_mfa_on_external_authentication(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enforceMfaOnExternalAuthentication"))

    @enforce_mfa_on_external_authentication.setter
    def enforce_mfa_on_external_authentication(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5499a6be20318ea28d14c1442185e4651e89a71d55cc88a390968e045a3a291)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforceMfaOnExternalAuthentication", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AuthenticationPolicyMfaPolicy]:
        return typing.cast(typing.Optional[AuthenticationPolicyMfaPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AuthenticationPolicyMfaPolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4543ed3976537106810551890f61efc7219ee2bbb40f09cf201056f9feac4fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyPatPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "default_expiry_in_days": "defaultExpiryInDays",
        "max_expiry_in_days": "maxExpiryInDays",
        "network_policy_evaluation": "networkPolicyEvaluation",
    },
)
class AuthenticationPolicyPatPolicy:
    def __init__(
        self,
        *,
        default_expiry_in_days: typing.Optional[jsii.Number] = None,
        max_expiry_in_days: typing.Optional[jsii.Number] = None,
        network_policy_evaluation: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_expiry_in_days: Specifies the default expiration time (in days) for a programmatic access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#default_expiry_in_days AuthenticationPolicy#default_expiry_in_days}
        :param max_expiry_in_days: Specifies the maximum number of days that can be set for the expiration time for a programmatic access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#max_expiry_in_days AuthenticationPolicy#max_expiry_in_days}
        :param network_policy_evaluation: Specifies the network policy evaluation for the PAT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#network_policy_evaluation AuthenticationPolicy#network_policy_evaluation}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5785fadbf3cf6a29fe0622bb405e49db7ee0e9c536741192992cc9c9c280bd3)
            check_type(argname="argument default_expiry_in_days", value=default_expiry_in_days, expected_type=type_hints["default_expiry_in_days"])
            check_type(argname="argument max_expiry_in_days", value=max_expiry_in_days, expected_type=type_hints["max_expiry_in_days"])
            check_type(argname="argument network_policy_evaluation", value=network_policy_evaluation, expected_type=type_hints["network_policy_evaluation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if default_expiry_in_days is not None:
            self._values["default_expiry_in_days"] = default_expiry_in_days
        if max_expiry_in_days is not None:
            self._values["max_expiry_in_days"] = max_expiry_in_days
        if network_policy_evaluation is not None:
            self._values["network_policy_evaluation"] = network_policy_evaluation

    @builtins.property
    def default_expiry_in_days(self) -> typing.Optional[jsii.Number]:
        '''Specifies the default expiration time (in days) for a programmatic access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#default_expiry_in_days AuthenticationPolicy#default_expiry_in_days}
        '''
        result = self._values.get("default_expiry_in_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_expiry_in_days(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum number of days that can be set for the expiration time for a programmatic access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#max_expiry_in_days AuthenticationPolicy#max_expiry_in_days}
        '''
        result = self._values.get("max_expiry_in_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def network_policy_evaluation(self) -> typing.Optional[builtins.str]:
        '''Specifies the network policy evaluation for the PAT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#network_policy_evaluation AuthenticationPolicy#network_policy_evaluation}
        '''
        result = self._values.get("network_policy_evaluation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthenticationPolicyPatPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthenticationPolicyPatPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyPatPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__790c1b329be9ca9288f1520ad595f344fde3513c2a70cc752a9ef47e60bd158b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDefaultExpiryInDays")
    def reset_default_expiry_in_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultExpiryInDays", []))

    @jsii.member(jsii_name="resetMaxExpiryInDays")
    def reset_max_expiry_in_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxExpiryInDays", []))

    @jsii.member(jsii_name="resetNetworkPolicyEvaluation")
    def reset_network_policy_evaluation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkPolicyEvaluation", []))

    @builtins.property
    @jsii.member(jsii_name="defaultExpiryInDaysInput")
    def default_expiry_in_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultExpiryInDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="maxExpiryInDaysInput")
    def max_expiry_in_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxExpiryInDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="networkPolicyEvaluationInput")
    def network_policy_evaluation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkPolicyEvaluationInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultExpiryInDays")
    def default_expiry_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultExpiryInDays"))

    @default_expiry_in_days.setter
    def default_expiry_in_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8324342492c9ab86db0fd8eb2f1995bace5afc9855c5c170e55917ac1d1e9ef3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultExpiryInDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxExpiryInDays")
    def max_expiry_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxExpiryInDays"))

    @max_expiry_in_days.setter
    def max_expiry_in_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e42ed1a5060ccfce19a862a9aa0bc9ad55e5e83a5dc9f08ece1b315f0ce67d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxExpiryInDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkPolicyEvaluation")
    def network_policy_evaluation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkPolicyEvaluation"))

    @network_policy_evaluation.setter
    def network_policy_evaluation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c26b1120ec02e64f379568d2bbc82a405f68eda5a84a6a4c64148988d9abc41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkPolicyEvaluation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AuthenticationPolicyPatPolicy]:
        return typing.cast(typing.Optional[AuthenticationPolicyPatPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AuthenticationPolicyPatPolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20ada1049120bb3e09544d2f622e6d8f19810ee1df03d183a069d3baf26207a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyShowOutput",
    jsii_struct_bases=[],
    name_mapping={},
)
class AuthenticationPolicyShowOutput:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthenticationPolicyShowOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthenticationPolicyShowOutputList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyShowOutputList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d69bf4d5f4410aaaa1817a2d7f6ff35a6d67b0f05b77581586d698f9c92171dd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AuthenticationPolicyShowOutputOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e01b98d28b81558b2c34a4f97c93c7b55259611fa410e9851eac152b78e35611)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AuthenticationPolicyShowOutputOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3099b419b2af09833bf3dcfac645740e395ed1faf6442f27ef999862dd690114)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc630b87ebe73267c7118d9a108aedc6496be176081c8db0d3da173e426da622)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b429d87f6d2dcc05c742feb056ece8f5d60883ada424fed74c255215f934f563)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class AuthenticationPolicyShowOutputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyShowOutputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a3344636ffeb7c85bd2398033c5418bea59d6f7c82bfeba2468495cbd00d18d)
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
    def internal_value(self) -> typing.Optional[AuthenticationPolicyShowOutput]:
        return typing.cast(typing.Optional[AuthenticationPolicyShowOutput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AuthenticationPolicyShowOutput],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__105bed7f87ca8fc73fb69c09a26086e40863d4c6304fc639cd3f96c0080c89ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "delete": "delete",
        "read": "read",
        "update": "update",
    },
)
class AuthenticationPolicyTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#create AuthenticationPolicy#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#delete AuthenticationPolicy#delete}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#read AuthenticationPolicy#read}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#update AuthenticationPolicy#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34969fd545703b6d91d3d86b9e174c0e23a4abfef5bb3b2461cddf7fc6950f03)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument read", value=read, expected_type=type_hints["read"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if read is not None:
            self._values["read"] = read
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#create AuthenticationPolicy#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#delete AuthenticationPolicy#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#read AuthenticationPolicy#read}.'''
        result = self._values.get("read")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#update AuthenticationPolicy#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthenticationPolicyTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthenticationPolicyTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0bfec72433203bdec12d27d007cfa0e7aaaa935fd8560dc42e706bff5d93cdbf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetRead")
    def reset_read(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRead", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="readInput")
    def read_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a18d8a003648c1f38ab0af70480dc6338e1b8cb791f1392daef2f70e3c37734)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6d502a61051c19f36a8732cff3fc400b7083f20770f7ffdc5e96934f97ef148)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="read")
    def read(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "read"))

    @read.setter
    def read(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1382ca315670180af883c24d6c6e7058a550967006f45a1375284074e793df1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "read", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e43f49f694ffed30f533b50af046105caca25ce6ded9f0ebdc25f325ba459c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthenticationPolicyTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthenticationPolicyTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthenticationPolicyTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fa71e327902ee3f016b4e51c5157587ab820d6488832aabe918daf99eec2787)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyWorkloadIdentityPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_aws_accounts": "allowedAwsAccounts",
        "allowed_azure_issuers": "allowedAzureIssuers",
        "allowed_oidc_issuers": "allowedOidcIssuers",
        "allowed_providers": "allowedProviders",
    },
)
class AuthenticationPolicyWorkloadIdentityPolicy:
    def __init__(
        self,
        *,
        allowed_aws_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_azure_issuers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_oidc_issuers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allowed_aws_accounts: Specifies the list of AWS account IDs allowed by the authentication policy during workload identity authentication of type ``AWS``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_aws_accounts AuthenticationPolicy#allowed_aws_accounts}
        :param allowed_azure_issuers: Specifies the list of Azure Entra ID issuers allowed by the authentication policy during workload identity authentication of type ``AZURE``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_azure_issuers AuthenticationPolicy#allowed_azure_issuers}
        :param allowed_oidc_issuers: Specifies the list of OIDC issuers allowed by the authentication policy during workload identity authentication of type ``OIDC``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_oidc_issuers AuthenticationPolicy#allowed_oidc_issuers}
        :param allowed_providers: Specifies the allowed providers for the workload identity policy. Valid values are: ``ALL`` | ``AWS`` | ``AZURE`` | ``GCP`` | ``OIDC``. These values are case-sensitive due to Terraform limitations (it's a nested field). Prefer using uppercased values. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_providers AuthenticationPolicy#allowed_providers}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f90e64aad0eb58da432f808df596e3d572f5087d8ecc392b8fbdcfeea974b04b)
            check_type(argname="argument allowed_aws_accounts", value=allowed_aws_accounts, expected_type=type_hints["allowed_aws_accounts"])
            check_type(argname="argument allowed_azure_issuers", value=allowed_azure_issuers, expected_type=type_hints["allowed_azure_issuers"])
            check_type(argname="argument allowed_oidc_issuers", value=allowed_oidc_issuers, expected_type=type_hints["allowed_oidc_issuers"])
            check_type(argname="argument allowed_providers", value=allowed_providers, expected_type=type_hints["allowed_providers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_aws_accounts is not None:
            self._values["allowed_aws_accounts"] = allowed_aws_accounts
        if allowed_azure_issuers is not None:
            self._values["allowed_azure_issuers"] = allowed_azure_issuers
        if allowed_oidc_issuers is not None:
            self._values["allowed_oidc_issuers"] = allowed_oidc_issuers
        if allowed_providers is not None:
            self._values["allowed_providers"] = allowed_providers

    @builtins.property
    def allowed_aws_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of AWS account IDs allowed by the authentication policy during workload identity authentication of type ``AWS``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_aws_accounts AuthenticationPolicy#allowed_aws_accounts}
        '''
        result = self._values.get("allowed_aws_accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_azure_issuers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of Azure Entra ID issuers allowed by the authentication policy during workload identity authentication of type ``AZURE``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_azure_issuers AuthenticationPolicy#allowed_azure_issuers}
        '''
        result = self._values.get("allowed_azure_issuers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_oidc_issuers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of OIDC issuers allowed by the authentication policy during workload identity authentication of type ``OIDC``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_oidc_issuers AuthenticationPolicy#allowed_oidc_issuers}
        '''
        result = self._values.get("allowed_oidc_issuers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_providers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the allowed providers for the workload identity policy.

        Valid values are: ``ALL`` | ``AWS`` | ``AZURE`` | ``GCP`` | ``OIDC``. These values are case-sensitive due to Terraform limitations (it's a nested field). Prefer using uppercased values.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.10.1/docs/resources/authentication_policy#allowed_providers AuthenticationPolicy#allowed_providers}
        '''
        result = self._values.get("allowed_providers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthenticationPolicyWorkloadIdentityPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthenticationPolicyWorkloadIdentityPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.authenticationPolicy.AuthenticationPolicyWorkloadIdentityPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__828fe247337f57f39b4daf7600fd1b985102f1ca574954c962c25a3192c816b2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowedAwsAccounts")
    def reset_allowed_aws_accounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedAwsAccounts", []))

    @jsii.member(jsii_name="resetAllowedAzureIssuers")
    def reset_allowed_azure_issuers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedAzureIssuers", []))

    @jsii.member(jsii_name="resetAllowedOidcIssuers")
    def reset_allowed_oidc_issuers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOidcIssuers", []))

    @jsii.member(jsii_name="resetAllowedProviders")
    def reset_allowed_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedProviders", []))

    @builtins.property
    @jsii.member(jsii_name="allowedAwsAccountsInput")
    def allowed_aws_accounts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedAwsAccountsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedAzureIssuersInput")
    def allowed_azure_issuers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedAzureIssuersInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedOidcIssuersInput")
    def allowed_oidc_issuers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOidcIssuersInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedProvidersInput")
    def allowed_providers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedProvidersInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedAwsAccounts")
    def allowed_aws_accounts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedAwsAccounts"))

    @allowed_aws_accounts.setter
    def allowed_aws_accounts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15e7c2a577afb45268a522968838442fe5a39c4812d035e1b67ab55354047556)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedAwsAccounts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedAzureIssuers")
    def allowed_azure_issuers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedAzureIssuers"))

    @allowed_azure_issuers.setter
    def allowed_azure_issuers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6f2e8441d103643f2144e52b65df15a8227f058c14184659ee52a2ae4522d85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedAzureIssuers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedOidcIssuers")
    def allowed_oidc_issuers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOidcIssuers"))

    @allowed_oidc_issuers.setter
    def allowed_oidc_issuers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08187a35b5a0f97d908ddc991adbcfe8bb560aa3596265b1cb9f1109c92faf36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedOidcIssuers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedProviders")
    def allowed_providers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedProviders"))

    @allowed_providers.setter
    def allowed_providers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ffa35f5abc18f73208f4e75269c3d7f28a413b4da846a0fa7d845cfd2e403fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedProviders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AuthenticationPolicyWorkloadIdentityPolicy]:
        return typing.cast(typing.Optional[AuthenticationPolicyWorkloadIdentityPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AuthenticationPolicyWorkloadIdentityPolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ee6ba359bc1d23d790dc1d9ab5cbd3a84ce1d5990c7dbc70ea242764beef03c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AuthenticationPolicy",
    "AuthenticationPolicyConfig",
    "AuthenticationPolicyDescribeOutput",
    "AuthenticationPolicyDescribeOutputList",
    "AuthenticationPolicyDescribeOutputOutputReference",
    "AuthenticationPolicyMfaPolicy",
    "AuthenticationPolicyMfaPolicyOutputReference",
    "AuthenticationPolicyPatPolicy",
    "AuthenticationPolicyPatPolicyOutputReference",
    "AuthenticationPolicyShowOutput",
    "AuthenticationPolicyShowOutputList",
    "AuthenticationPolicyShowOutputOutputReference",
    "AuthenticationPolicyTimeouts",
    "AuthenticationPolicyTimeoutsOutputReference",
    "AuthenticationPolicyWorkloadIdentityPolicy",
    "AuthenticationPolicyWorkloadIdentityPolicyOutputReference",
]

publication.publish()

def _typecheckingstub__77fb43a6a2493a8f92aa71cb59dc9a6e0cfce86f9a13283202805d7546a826ef(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    database: builtins.str,
    name: builtins.str,
    schema: builtins.str,
    authentication_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
    client_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    comment: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    mfa_authentication_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
    mfa_enrollment: typing.Optional[builtins.str] = None,
    mfa_policy: typing.Optional[typing.Union[AuthenticationPolicyMfaPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    pat_policy: typing.Optional[typing.Union[AuthenticationPolicyPatPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    security_integrations: typing.Optional[typing.Sequence[builtins.str]] = None,
    timeouts: typing.Optional[typing.Union[AuthenticationPolicyTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    workload_identity_policy: typing.Optional[typing.Union[AuthenticationPolicyWorkloadIdentityPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__c6196c97cfd956988d42d4f42ab1e2de4d23cfae668004274fbb54db2d87fb6c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a211ec24767dd0d401bb98fa7d194b2221fa72c3133498be2aa0aecc7ab4bb3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13b9316f3a70730e242f6ca2f064bc959681edff21bced6f8ce94fae70bec8cf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec4bf234d4484ea595b7f5848c79ec1fd41c9fcee1d01647a75dd98d55069194(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dd1d000687e04454751c29eeeea8f9b64a027553d018d5cbf5bd954babe7bcd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50a045c0a965a8550ad6bc387d3f70ed02261ae16cf2e880ecc38ecca3e73c0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40c44db153fbfbdb186cafdfe5acf41c1000ddc3170b34294282fae10553dfed(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__559ce969d56d5037f3cec06daa7f95057163249486b2d526e67bba524f42885f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97bfe888ebb1a5e3d5f87558d866dd3ad6dc5e61c738d6478a2dd8c1680e12af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c10433f3a590b5ddf7af1c7bec2bf37665cce3716108abbade8ad02cc0317097(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__795a742bbc7bf6a7b5b005e6d8bc3ab8694dc7e6eb67b1904e6a9589f3a704ff(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a119c304710bb6ee35cd6eec8be3372b24fec526b4232b6e5b6716f46a4dc15d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    database: builtins.str,
    name: builtins.str,
    schema: builtins.str,
    authentication_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
    client_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    comment: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    mfa_authentication_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
    mfa_enrollment: typing.Optional[builtins.str] = None,
    mfa_policy: typing.Optional[typing.Union[AuthenticationPolicyMfaPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    pat_policy: typing.Optional[typing.Union[AuthenticationPolicyPatPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    security_integrations: typing.Optional[typing.Sequence[builtins.str]] = None,
    timeouts: typing.Optional[typing.Union[AuthenticationPolicyTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    workload_identity_policy: typing.Optional[typing.Union[AuthenticationPolicyWorkloadIdentityPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__020e99a3ea32e58034c052cc3a12e7f37bfb82fe1dd8b78d5812d66d28d4bfae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34d34877a162e0680b21cbd6384aa0323213d364dde4ae03ec6358550f32d313(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af05419ad3dbf8bbc1fedccf5e0722076c7ad7bca4294173a8c4ce70214e884f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ddec069b41852a09df25f3526d1e3e047b3753485d3f5244a71646eee29d7ff(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c42a2133ea2c219e22efc2d6c52741a4c1814c378a933b46219a597c04e2704(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fc33d50d2c4660072d3f40595c2478b92e662b97fbe3799fd036988fee175b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08a72904a1a894519b701d3202d951b1fe6fecd88de7d1f65edf91247b78283d(
    value: typing.Optional[AuthenticationPolicyDescribeOutput],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abcecfc354f2e4198a8936aa1ec3fbb23344f64890354d3181c0113fbae9e731(
    *,
    allowed_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
    enforce_mfa_on_external_authentication: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a7d0adf7a0640a9f07cba0c88757c5f2e26b2f30b0bfab3c6c32933cc9d3255(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__180afcbd0b1f037e084e3b71f60fae2369f14a52856af80bbcb9c058b434fd95(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5499a6be20318ea28d14c1442185e4651e89a71d55cc88a390968e045a3a291(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4543ed3976537106810551890f61efc7219ee2bbb40f09cf201056f9feac4fa(
    value: typing.Optional[AuthenticationPolicyMfaPolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5785fadbf3cf6a29fe0622bb405e49db7ee0e9c536741192992cc9c9c280bd3(
    *,
    default_expiry_in_days: typing.Optional[jsii.Number] = None,
    max_expiry_in_days: typing.Optional[jsii.Number] = None,
    network_policy_evaluation: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__790c1b329be9ca9288f1520ad595f344fde3513c2a70cc752a9ef47e60bd158b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8324342492c9ab86db0fd8eb2f1995bace5afc9855c5c170e55917ac1d1e9ef3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e42ed1a5060ccfce19a862a9aa0bc9ad55e5e83a5dc9f08ece1b315f0ce67d5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c26b1120ec02e64f379568d2bbc82a405f68eda5a84a6a4c64148988d9abc41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20ada1049120bb3e09544d2f622e6d8f19810ee1df03d183a069d3baf26207a8(
    value: typing.Optional[AuthenticationPolicyPatPolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d69bf4d5f4410aaaa1817a2d7f6ff35a6d67b0f05b77581586d698f9c92171dd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e01b98d28b81558b2c34a4f97c93c7b55259611fa410e9851eac152b78e35611(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3099b419b2af09833bf3dcfac645740e395ed1faf6442f27ef999862dd690114(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc630b87ebe73267c7118d9a108aedc6496be176081c8db0d3da173e426da622(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b429d87f6d2dcc05c742feb056ece8f5d60883ada424fed74c255215f934f563(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a3344636ffeb7c85bd2398033c5418bea59d6f7c82bfeba2468495cbd00d18d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__105bed7f87ca8fc73fb69c09a26086e40863d4c6304fc639cd3f96c0080c89ed(
    value: typing.Optional[AuthenticationPolicyShowOutput],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34969fd545703b6d91d3d86b9e174c0e23a4abfef5bb3b2461cddf7fc6950f03(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    read: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bfec72433203bdec12d27d007cfa0e7aaaa935fd8560dc42e706bff5d93cdbf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a18d8a003648c1f38ab0af70480dc6338e1b8cb791f1392daef2f70e3c37734(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6d502a61051c19f36a8732cff3fc400b7083f20770f7ffdc5e96934f97ef148(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1382ca315670180af883c24d6c6e7058a550967006f45a1375284074e793df1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e43f49f694ffed30f533b50af046105caca25ce6ded9f0ebdc25f325ba459c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fa71e327902ee3f016b4e51c5157587ab820d6488832aabe918daf99eec2787(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthenticationPolicyTimeouts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f90e64aad0eb58da432f808df596e3d572f5087d8ecc392b8fbdcfeea974b04b(
    *,
    allowed_aws_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_azure_issuers: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_oidc_issuers: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__828fe247337f57f39b4daf7600fd1b985102f1ca574954c962c25a3192c816b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15e7c2a577afb45268a522968838442fe5a39c4812d035e1b67ab55354047556(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6f2e8441d103643f2144e52b65df15a8227f058c14184659ee52a2ae4522d85(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08187a35b5a0f97d908ddc991adbcfe8bb560aa3596265b1cb9f1109c92faf36(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ffa35f5abc18f73208f4e75269c3d7f28a413b4da846a0fa7d845cfd2e403fb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ee6ba359bc1d23d790dc1d9ab5cbd3a84ce1d5990c7dbc70ea242764beef03c(
    value: typing.Optional[AuthenticationPolicyWorkloadIdentityPolicy],
) -> None:
    """Type checking stubs"""
    pass
