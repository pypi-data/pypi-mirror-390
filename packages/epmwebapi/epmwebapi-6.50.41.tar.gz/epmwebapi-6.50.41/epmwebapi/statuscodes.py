from enum import Enum

# <summary>
# Common UA StatusCodes
# </summary>
class StatusCodes(Enum):
    """
    Enumeration with common OPC UA status codes.
    """
    # <summary>
    # An unexpected error occurred.
    # </summary>
    BadUnexpectedError = 0x80010000
    """
    An unexpected error occurred.
    """

    # <summary>
    # An internal error occurred as a result of a programming or configuration error.
    # </summary>
    BadInternalError = 0x80020000
    """
    An internal error occurred as a result of a programming or configuration error.
    """
    # <summary>
    # Not enough memory to complete the operation.
    # </summary>
    BadOutOfMemory = 0x80030000
    """
    Not enough memory to complete this operation.
    """
    # <summary>
    # An operating system resource is not available.
    # </summary>
    BadResourceUnavailable = 0x80040000
    """
    A resource of the operating system is not available.
    """
    # <summary>
    # A low level communication error occurred.
    # </summary>
    BadCommunicationError = 0x80050000
    """
    A low level communication error occurred.
    """
    # <summary>
    # Encoding halted because of invalid data in the objects being serialized.
    # </summary>
    BadEncodingError = 0x80060000
    """
    Encoding halted because of invalid data in the objects being serialized.
    """
    # <summary>
    # Decoding halted because of invalid data in the stream.
    # </summary>
    BadDecodingError = 0x80070000
    """
    Decoding halted because of invalid data in the stream.
    """
    # <summary>
    # The message encoding/decoding limits imposed by the stack have been exceeded.
    # </summary>
    BadEncodingLimitsExceeded = 0x80080000
    """
    The limits of encoding or decoding messages imposed by the stack were exceeded.
    """
    # <summary>
    # The request message size exceeds limits set by the server.
    # </summary>
    BadRequestTooLarge = 0x80B80000
    """
    Size of request message exceeds the limits imposed by the server.
    """
    # <summary>
    # The response message size exceeds limits set by the client.
    # </summary>
    BadResponseTooLarge = 0x80B90000
    """
    Size of response message exceeds the limits imposed by the client.
    """
    # <summary>
    # An unrecognized response was received from the server.
    # </summary>
    BadUnknownResponse = 0x80090000
    """
    An unrecognized response was received from the server.
    """
    # <summary>
    # The operation timed out.
    # </summary>
    BadTimeout = 0x800A0000
    """
    Operation timed out.
    """
    # <summary>
    # The server does not support the requested service.
    # </summary>
    BadServiceUnsupported = 0x800B0000
    """
    Server does not support the requested service.
    """
    # <summary>
    # The operation was cancelled because the application is shutting down.
    # </summary>
    BadShutdown = 0x800C0000
    """
    Operation cancelled because application is shutting down.
    """
    # <summary>
    # The operation could not complete because the client is not connected to the server.
    # </summary>
    BadServerNotConnected = 0x800D0000
    """
    Operation could not complete because client is not connected to server.
    """
    # <summary>
    # The server has stopped and cannot process any requests.
    # </summary>
    BadServerHalted = 0x800E0000
    """
    Server stopped and cannot process any requests.
    """
    # <summary>
    # There was nothing to do because the client passed a list of operations with no elements.
    # </summary>
    BadNothingToDo = 0x800F0000
    """
    Nothing to do because client passed a list of operations without elements.
    """
    # <summary>
    # The request could not be processed because it specified too many operations.
    # </summary>
    BadTooManyOperations = 0x80100000
    """
    Request could not be processed because it specifies too many operations.
    """
    # <summary>
    # The extension object cannot be (de)serialized because the data type id is not recognized.
    # </summary>
    BadDataTypeIdUnknown = 0x80110000
    """
    Extension object cannot be serialized or deserialized because data type ID is not recognized.
    """
    # <summary>
    # The certificate provided as a parameter is not valid.
    # </summary>
    BadCertificateInvalid = 0x80120000
    """
    Provided certificate as a parameter is not valid.
    """
    # <summary>
    # An error occurred verifying security.
    # </summary>
    BadSecurityChecksFailed = 0x80130000
    """
    An error occurred while verifying security.
    """
    # <summary>
    # The Certificate has expired or is not yet valid.
    # </summary>
    BadCertificateTimeInvalid = 0x80140000
    """
    Certificate expired or it is not yet valid.
    """
    # <summary>
    # An Issuer Certificate has expired or is not yet valid.
    # </summary>
    BadCertificateIssuerTimeInvalid = 0x80150000
    """
    Certificate Issuer expired or it is not yet valid.
    """
    # <summary>
    # The HostName used to connect to a Server does not match a HostName in the Certificate.
    # </summary>
    BadCertificateHostNameInvalid = 0x80160000
    """
    Hostname used to connect to server does not match Hostname in the certificate.
    """
    # <summary>
    # The URI specified in the ApplicationDescription does not match the URI in the Certificate.
    # </summary>
    BadCertificateUriInvalid = 0x80170000
    """
    Specified URI in ApplicationDescription does not match URI in the certificate.
    """
    # <summary>
    # The Certificate may not be used for the requested operation.
    # </summary>
    BadCertificateUseNotAllowed = 0x80180000
    """
    Certificate cannot be used for the requested operation.
    """
    # <summary>
    # The Issuer Certificate may not be used for the requested operation.
    # </summary>
    BadCertificateIssuerUseNotAllowed = 0x80190000
    """
    Certificate Issuer cannot be used for the requested operation.
    """
    # <summary>
    # The Certificate is not trusted.
    # </summary>
    BadCertificateUntrusted = 0x801A0000
    """
    Certificate is not trusted.
    """
    # <summary>
    # It was not possible to determine if the Certificate has been revoked.
    # </summary>
    BadCertificateRevocationUnknown = 0x801B0000
    """
    Cannot determine whether the certificate was revoked or not.
    """
    # <summary>
    # It was not possible to determine if the Issuer Certificate has been revoked.
    # </summary>
    BadCertificateIssuerRevocationUnknown = 0x801C0000
    """
    Cannot determine whether Certificate Issuer was revoked or not.
    """
    # <summary>
    # The Certificate has been revoked.
    # </summary>
    BadCertificateRevoked = 0x801D0000
    """
    Certificate was revoked.
    """
    # <summary>
    # The Issuer Certificate has been revoked.
    # </summary>
    BadCertificateIssuerRevoked = 0x801E0000
    """
    Certificate Issuer was revoked.
    """
    # <summary>
    # User does not have permission to perform the requested operation.
    # </summary>
    BadUserAccessDenied = 0x801F0000
    """
    User does not have permission to perform the requested operation.
    """
    # <summary>
    # The user identity token is not valid.
    # </summary>
    BadIdentityTokenInvalid = 0x80200000
    """
    User's identity token is not valid.
    """
    # <summary>
    # The user identity token is valid but the server has rejected it.
    # </summary>
    BadIdentityTokenRejected = 0x80210000
    """
    User's identity token is valid but the server rejected it.
    """
    # <summary>
    # The specified secure channel is not longer valid.
    # </summary>
    BadSecureChannelIdInvalid = 0x80220000
    """
    Specified secure channel is no longer valid.
    """
    # <summary>
    # The timestamp is outside the range allowed by the server.
    # </summary>
    BadInvalidTimestamp = 0x80230000
    """
    Timestamp outside server's allowed range.
    """
    # <summary>
    # The nonce does appear to be not a random value or it is not the correct length.
    # </summary>
    BadNonceInvalid = 0x80240000
    """
    Nonce does not appear to be a random value or does not have the correct length.
    """
    # <summary>
    # The session id is not valid.
    # </summary>
    BadSessionIdInvalid = 0x80250000
    """
    Session ID is not valid.
    """
    # <summary>
    # The session was closed by the client.
    # </summary>
    BadSessionClosed = 0x80260000
    """
    Session was closed by the client.
    """
    # <summary>
    # The session cannot be used because ActivateSession has not been called.
    # </summary>
    BadSessionNotActivated = 0x80270000
    """
    Session cannot be used because ActivateSession was not called.
    """
    # <summary>
    # The subscription id is not valid.
    # </summary>
    BadSubscriptionIdInvalid = 0x80280000
    """
    Subscription ID is not valid.
    """
    # <summary>
    # The header for the request is missing or invalid.
    # </summary>
    BadRequestHeaderInvalid = 0x802A0000
    """
    Request header is missing or invalid.
    """
    # <summary>
    # The timestamps to return parameter is invalid.
    # </summary>
    BadTimestampsToReturnInvalid = 0x802B0000
    """
    Timestamps to return are invalid.
    """
    # <summary>
    # The request was cancelled by the client.
    # </summary>
    BadRequestCancelledByClient = 0x802C0000
    """
    Request cancelled by the client.
    """
    # <summary>
    # The subscription was transferred to another session.
    # </summary>
    GoodSubscriptionTransferred = 0x002D0000
    """
    Subscription was transferred to another session.
    """
    # <summary>
    # The processing will complete asynchronously.
    # </summary>
    GoodCompletesAsynchronously = 0x002E0000
    """
    Processing will be completed asynchronously.
    """
    # <summary>
    # Sampling has slowed down due to resource limitations.
    # </summary>
    GoodOverload = 0x002F0000
    """
    Sampling slowed down due to resource limitations.
    """
    # <summary>
    # The value written was accepted but was clamped.
    # </summary>
    GoodClamped = 0x00300000
    """
    Written value was accepted but clamped.
    """
    # <summary>
    # Communication with the data source is defined, but not established, and there is no last known value available.
    # </summary>
    BadNoCommunication = 0x80310000
    """
    Communication with data source is defined but not established, and there is no last known value available.
    """
    # <summary>
    # Waiting for the server to obtain values from the underlying data source.
    # </summary>
    BadWaitingForInitialData = 0x80320000
    """
    Waiting for the server to obtain values from the underlying data source.
    """
    # <summary>
    # The syntax of the node id is not valid.
    # </summary>
    BadNodeIdInvalid = 0x80330000
    """
    Syntax of node ID is not valid.
    """
    # <summary>
    # The node id refers to a node that does not exist in the server address space.
    # </summary>
    BadNodeIdUnknown = 0x80340000
    """
    Node ID refers to a node that does not exist in the server's address space.
    """
    # <summary>
    # The attribute is not supported for the specified Node.
    # </summary>
    BadAttributeIdInvalid = 0x80350000
    """
    Attribute is not supported for the specified node.
    """
    # <summary>
    # The syntax of the index range parameter is invalid.
    # </summary>
    BadIndexRangeInvalid = 0x80360000
    """
    Syntax of index range parameter is invalid.
    """
    # <summary>
    # No data exists within the range of indexes specified.
    # </summary>
    BadIndexRangeNoData = 0x80370000
    """
    There is no data in the specified range of indexes.
    """
    # <summary>
    # The data encoding is invalid.
    # </summary>
    BadDataEncodingInvalid = 0x80380000
    """
    Data encoding is invalid.
    """
    # <summary>
    # The server does not support the requested data encoding for the node.
    # </summary>
    BadDataEncodingUnsupported = 0x80390000
    """
    Server does not support the requested data encoding for the node.
    """
    # <summary>
    # The access level does not allow reading or subscribing to the Node.
    # </summary>
    BadNotReadable = 0x803A0000
    """
    Access level does not allow reading or subscribing to the node.
    """
    # <summary>
    # The access level does not allow writing to the Node.
    # </summary>
    BadNotWritable = 0x803B0000
    """
    Access level does not allow writing to the node.
    """
    # <summary>
    # The value was out of range.
    # </summary>
    BadOutOfRange = 0x803C0000
    """
    Value is out of range.
    """
    # <summary>
    # The requested operation is not supported.
    # </summary>
    BadNotSupported = 0x803D0000
    """
    Requested operation is not supported.
    """
    # <summary>
    # A requested item was not found or a search operation ended without success.
    # </summary>
    BadNotFound = 0x803E0000
    """
    Requested item not found or a search operation ended without success.
    """
    # <summary>
    # The object cannot be used because it has been deleted.
    # </summary>
    BadObjectDeleted = 0x803F0000
    """
    Object cannot be used because it was deleted.
    """
    # <summary>
    # Requested operation is not implemented.
    # </summary>
    BadNotImplemented = 0x80400000
    """
    Requested operation is not implemented.
    """
    # <summary>
    # The monitoring mode is invalid.
    # </summary>
    BadMonitoringModeInvalid = 0x80410000
    """
    Invalid monitoring mode.
    """
    # <summary>
    # The monitoring item id does not refer to a valid monitored item.
    # </summary>
    BadMonitoredItemIdInvalid = 0x80420000
    """
    Monitored item ID does not refer to a valid monitored item.
    """
    # <summary>
    # The monitored item filter parameter is not valid.
    # </summary>
    BadMonitoredItemFilterInvalid = 0x80430000
    """
    Monitored item filter is not valid.
    """
    # <summary>
    # The server does not support the requested monitored item filter.
    # </summary>
    BadMonitoredItemFilterUnsupported = 0x80440000
    """
    Server does not support the requested monitored item filter.
    """
    # <summary>
    # A monitoring filter cannot be used in combination with the attribute specified.
    # </summary>
    BadFilterNotAllowed = 0x80450000
    """
    Monitored filter cannot be used together with the specified attribute.
    """
    # <summary>
    # A mandadatory structured parameter was missing or null.
    # </summary>
    BadStructureMissing = 0x80460000
    """
    Mandatory structure is missing or null.
    """
    # <summary>
    # The event filter is not valid.
    # </summary>
    BadEventFilterInvalid = 0x80470000
    """
    Invalid event filter.
    """
    # <summary>
    # The content filter is not valid.
    # </summary>
    BadContentFilterInvalid = 0x80480000
    """
    Invalid content filter.
    """
    # <summary>
    # An unregognized operator was provided in a filter.
    # </summary>
    BadFilterOperatorInvalid = 0x80C10000
    """
    Unrecognized operator provided in a filter.
    """
    # <summary>
    # A valid operator was provided, but the server does not provide support for this filter operator.
    # </summary>
    BadFilterOperatorUnsupported = 0x80C20000
    """
    Valid operator provided, but the server does not support that filter operator.
    """
    # <summary>
    # The number of operands provided for the filter operator was less then expected for the operand provided.
    # </summary>
    BadFilterOperandCountMismatch = 0x80C30000
    """
    Number of operands provided for filter operator is less than expected for that operand.
    """
    # <summary>
    # The operand used in a content filter is not valid.
    # </summary>
    BadFilterOperandInvalid = 0x80490000
    """
    Operand used in a content filter is not valid.
    """
    # <summary>
    # The referenced element is not a valid element in the content filter.
    # </summary>
    BadFilterElementInvalid = 0x80C40000
    """
    Referenced element is not valid in the content filter.
    """
    # <summary>
    # The referenced literal is not a valid value.
    # </summary>
    BadFilterLiteralInvalid = 0x80C50000
    """
    Referenced literal is an invalid value.
    """
    # <summary>
    # The continuation point provide is longer valid.
    # </summary>
    BadContinuationPointInvalid = 0x804A0000
    """
    Provided continuation point is invalid.
    """
    # <summary>
    # The operation could not be processed because all continuation points have been allocated.
    # </summary>
    BadNoContinuationPoints = 0x804B0000
    """
    Operation could not be processed because all continuation points were allocated.
    """
    # <summary>
    # The operation could not be processed because all continuation points have been allocated.
    # </summary>
    BadReferenceTypeIdInvalid = 0x804C0000
    """
    Operation could not be processed because all continuation points were allocated.
    """
    # <summary>
    # The browse direction is not valid.
    # </summary>
    BadBrowseDirectionInvalid = 0x804D0000
    """
    Invalid browse direction.
    """
    # <summary>
    # 	The node is not part of the view.
    # </summary>
    BadNodeNotInView = 0x804E0000
    """
    Node is not part of view.
    """
    # <summary>
    # The ServerUri is not a valid URI.
    # </summary>
    BadServerUriInvalid = 0x804F0000
    """
    ServerUri is not a valid URI.
    """
    # <summary>
    # No ServerName was specified.
    # </summary>
    BadServerNameMissing = 0x80500000
    """
    Servername was not specified.
    """
    # <summary>
    # No DiscoveryUrl was specified.
    # </summary>
    BadDiscoveryUrlMissing = 0x80510000
    """
    DiscoveryUrl was not specified.
    """
    # <summary>
    # The semaphore file specified by the client is not valid.
    # </summary>
    BadSempahoreFileMissing = 0x80520000
    """
    Semaphore file specified by the client is invalid.
    """
    # <summary>
    # The security token request type is not valid.
    # </summary>
    BadRequestTypeInvalid = 0x80530000
    """
    Security token's request type is invalid.
    """
    # <summary>
    # The security mode does not meet the requirements set by the Server.
    # </summary>
    BadSecurityModeRejected = 0x80540000
    """
    Security mode does not match server requirements.
    """
    # <summary>
    # The security policy does not meet the requirements set by the Server.
    # </summary>
    BadSecurityPolicyRejected = 0x80550000
    """
    Security policy does not match server requirements.
    """
    # <summary>
    # The server has reached its maximum number of sessions.
    # </summary>
    BadTooManySessions = 0x80560000
    """
    Server reached its maximum number of sessions.
    """
    # <summary>
    # The user token signature is missing or invalid.
    # </summary>
    BadUserSignatureInvalid = 0x80570000
    """
    User's token signature is missing or invalid.
    """
    # <summary>
    # The signature generated with the client certificate is missing or invalid.
    # </summary>
    BadApplicationSignatureInvalid = 0x80580000
    """
    Signature generated with client's certificate is missing or invalid.
    """
    # <summary>
    # The client did not provide at least one software certificate that is valid and meets the profile requirements for the server.
    # </summary>
    BadNoValidCertificates = 0x80590000
    """
    Client did not provide at least one valid software certificate that matches the server's profile requirements.
    """
    # <summary>
    # The Server does not support changing the user identity assigned to the session.
    # </summary>
    BadIdentityChangeNotSupported = 0x80C60000
    """
    Server does not support changing user's identity assigned to session.
    """
    # <summary>
    # The request was cancelled by the client with the Cancel service.
    # </summary>
    BadRequestCancelledByRequest = 0x805A0000
    """
    Request cancelled by the client using the cancel service.
    """
    # <summary>
    # The parent node id does not to refer to a valid node.
    # </summary>
    BadParentNodeIdInvalid = 0x805B0000
    """
    Parent node ID does not refer to a valid node.
    """
    # <summary>
    # The reference could not be created because it violates constraints imposed by the data model.
    # </summary>
    BadReferenceNotAllowed = 0x805C0000
    """
    Reference could not be created because it violates constraints imposed by data model.
    """
    # <summary>
    # The requested node id was reject because it was either invalid or server does not allow node ids to be specified by the client.
    # </summary>
    BadNodeIdRejected = 0x805D0000
    """
    Requested node ID rejected because it was either invalid or the server does not allow client-specified node IDs.
    """
    # <summary>
    # The requested node id is already used by another node.
    # </summary>
    BadNodeIdExists = 0x805E0000
    """
    Requested node ID already in use by another node.
    """
    # <summary>
    # The node class is not valid.
    # </summary>
    BadNodeClassInvalid = 0x805F0000
    """
    Invalid node class.
    """
    # <summary>
    # The browse name is invalid.
    # </summary>
    BadBrowseNameInvalid = 0x80600000
    """
    Invalid browse name.
    """
    # <summary>
    # The browse name is not unique among nodes that share the same relationship with the parent.
    # </summary>
    BadBrowseNameDuplicated = 0x80610000
    """
    Browse name is not unique among nodes that share the same relationship with parent.
    """
    # <summary>
    # The node attributes are not valid for the node class.
    # </summary>
    BadNodeAttributesInvalid = 0x80620000
    """
    Invalid node attributes for the node class.
    """
    # <summary>
    # The type definition node id does not reference an appropriate type node.
    # </summary>
    BadTypeDefinitionInvalid = 0x80630000
    """
    Node ID's type definition does not reference an appropriate node type.
    """
    # <summary>
    # The source node id does reference a valid node.
    # </summary>
    BadSourceNodeIdInvalid = 0x80640000
    """
    Source node ID does not reference a valid node.
    """
    # <summary>
    # The target node id does reference a valid node.
    # </summary>
    BadTargetNodeIdInvalid = 0x80650000
    """
    Target node ID does not reference a valid node.
    """
    # <summary>
    # The reference type between the nodes is already defined.
    # </summary>
    BadDuplicateReferenceNotAllowed = 0x80660000
    """
    Reference type between nodes already defined.
    """
    # <summary>
    # The server does not allow this type of self reference on this node.
    # </summary>
    BadInvalidSelfReference = 0x80670000
    """
    Server does not allow this type of self-reference on this node.
    """
    # <summary>
    # The reference type is not valid for a reference to a remote server.
    # </summary>
    BadReferenceLocalOnly = 0x80680000
    """
    Invalid reference type for a reference to a remote server.
    """
    # <summary>
    # The server will not allow the node to be deleted.
    # </summary>
    BadNoDeleteRights = 0x80690000
    """
    Server does not allow deleting this node.
    """
    # <summary>
    # The server was not able to delete all target references.
    # </summary>
    UncertainReferenceNotDeleted = 0x40BC0000
    """
    Server could not delete all target references.
    """
    # <summary>
    # The server index is not valid.
    # </summary>
    BadServerIndexInvalid = 0x806A0000
    """
    Invalid server index.
    """
    # <summary>
    # The view id does not refer to a valid view node.
    # </summary>
    BadViewIdUnknown = 0x806B0000
    """
    View ID does not refer to a valid view node.
    """
    # <summary>
    # The view timestamp is not available or not supported.
    # </summary>
    BadViewTimestampInvalid = 0x80C90000
    """
    View's timestamp is not available or not supported.
    """
    # <summary>
    # The view parameters are not consistent withe each other.
    # </summary>
    BadViewParameterMismatch = 0x80CA0000
    """
    View parameters are not consistent with each other.
    """
    # <summary>
    # The view version is not available or not supported.
    # </summary>
    BadViewVersionInvalid = 0x80CB0000
    """
    View version is not available or not supported.
    """
    # <summary>
    # The list of references may not be complete because the underlying system is not available.
    # </summary>
    UncertainNotAllNodesAvailable = 0x40C00000
    """
    List of references may not be complete because the underlying system is not available.
    """
    # <summary>
    # The server should have followed a reference to a node in a remote server but did not. The result set may be incomplete.
    # </summary>
    GoodResultsMayBeIncomplete = 0x00BA0000
    """
    Server should have followed a reference to a node in a remote server but it did not. Result set may be incomplete.
    """
    # <summary>
    # The provided Nodeid was not a type definition nodeid.
    # </summary>
    BadNotTypeDefinition = 0x80C80000
    """
    Provided Nodeid is not a type definition nodeid.
    """
    # <summary>
    # One of the references to follow in the relative path references to a node in the address space in another server.
    # </summary>
    UncertainReferenceOutOfServer = 0x406C0000
    """
    One of the references to follow in the relative path references a node in the address space in another server.
    """
    # <summary>
    # The requested operation has too many matches to return.
    # </summary>
    BadTooManyMatches = 0x806D0000
    """
    Requested operation contains too many matches to return.
    """
    # <summary>
    # The requested operation requires too many resources in the server.
    # </summary>
    BadQueryTooComplex = 0x806E0000
    """
    Requested operation requires too many server resources.
    """
    # <summary>
    # The requested operation has no match to return.
    # </summary>
    BadNoMatch = 0x806F0000
    """
    Requested operation contains no matches to return.
    """
    # <summary>
    # The max age parameter is invalid.
    # </summary>
    BadMaxAgeInvalid = 0x80700000
    """
    Invalid maximum age.
    """
    # <summary>
    # The history details parameter is not valid.
    # </summary>
    BadHistoryOperationInvalid = 0x80710000
    """
    Invalid history details.
    """
    # <summary>
    # The server does not support the requested operation.
    # </summary>
    BadHistoryOperationUnsupported = 0x80720000
    """
    Server does not support requested operation.
    """
    # <summary>
    # The defined timestamp to return was invalid.
    # </summary>
    BadInvalidTimestampArgument = 0x80BD0000
    """
    Invalid timestamp.
    """
    # <summary>
    # The server does support writing the combination of value, status and timestamps provided.
    # </summary>
    BadWriteNotSupported = 0x80730000
    """
    Server does not support writing the provided combination of value, status, and timestamp.
    """
    # <summary>
    # The value supplied for the attribute is not of the same type as the attribute's value.
    # </summary>
    BadTypeMismatch = 0x80740000
    """
    Supplied value for the attribute does not have the same type of attribute's value.
    """
    # <summary>
    # The method id does not refer to a method for the specified object.
    # </summary>
    BadMethodInvalid = 0x80750000
    """
    Method ID does not refer to a method for the specified object.
    """
    # <summary>
    # The client did not specify all of the input arguments for the method.
    # </summary>
    BadArgumentsMissing = 0x80760000
    """
    Client did not specify all input arguments of the method.
    """
    # <summary>
    # The server has reached its  maximum number of subscriptions.
    # </summary>
    BadTooManySubscriptions = 0x80770000
    """
    Server reached its maximum number of subscriptions.
    """
    # <summary>
    # The server has reached the maximum number of queued publish requests.
    # </summary>
    BadTooManyPublishRequests = 0x80780000
    """
    Server reached its maximum number of queued-publish requests.
    """
    # <summary>
    # There is no subscription available for this session.
    # </summary>
    BadNoSubscription = 0x80790000
    """
    No subscription available for this session.
    """
    # <summary>
    # The sequence number is unknown to the server.
    # </summary>
    BadSequenceNumberUnknown = 0x807A0000
    """
    Sequence number is unknown to the server.
    """
    # <summary>
    # The requested notification message is no longer available.
    # </summary>
    BadMessageNotAvailable = 0x807B0000
    """
    Requested notification message is no longer available.
    """
    # <summary>
    # The Client of the current Session does not support one or more Profiles that are necessary for the Subscription.
    # </summary>
    BadInsufficientClientProfile = 0x807C0000
    """
    Client of the current session does not support one or more profiles necessary for subscription.
    """
    # <summary>
    # The sub-state machine is not currently active.
    # </summary>
    BadStateNotActive = 0x80BF0000
    """
    Sub-state machine not currently active.
    """
    # <summary>
    # The server cannot process the request because it is too busy.
    # </summary>
    BadTcpServerTooBusy = 0x807D0000
    """
    Server cannot process request becaus it is too busy.
    """
    # <summary>
    # The type of the message specified in the header invalid.
    # </summary>
    BadTcpMessageTypeInvalid = 0x807E0000
    """
    Invalid type specified in message's header.
    """
    # <summary>
    # The SecureChannelId and/or TokenId are not currently in use.
    # </summary>
    BadTcpSecureChannelUnknown = 0x807F0000
    """
    SecureChannelId or TokenId are not currently in use.
    """
    # <summary>
    # The size of the message specified in the header is too large.
    # </summary>
    BadTcpMessageTooLarge = 0x80800000
    """
    Size specified in message's header is too large.
    """
    # <summary>
    # There are not enough resources to process the request.
    # </summary>
    BadTcpNotEnoughResources = 0x80810000
    """
    Not enough resources to process request.
    """
    # <summary>
    # An internal error occurred.
    # </summary>
    BadTcpInternalError = 0x80820000
    """
    Internal error occurred.
    """
    # <summary>
    # he Server does not recognize the QueryString specified.
    # </summary>
    BadTcpEndpointUrlInvalid = 0x80830000
    """
    Server does not recognize the specified query string.
    """
    # <summary>
    # The request could not be sent because of a network interruption.
    # </summary>
    BadRequestInterrupted = 0x80840000
    """
    Request could not be set due to a network interruption.
    """
    # <summary>
    # Timeout occurred while processing the request.
    # </summary>
    BadRequestTimeout = 0x80850000
    """
    Time-out occurred while processing request.
    """
    # <summary>
    # The secure channel has been closed.
    # </summary>
    BadSecureChannelClosed = 0x80860000
    """
    Secure channel was closed.
    """
    # <summary>
    # The token has expired or is not recognized.
    # </summary>
    BadSecureChannelTokenUnknown = 0x80870000
    """
    Expired token or it is not recognized.
    """
    # <summary>
    # The sequence number is not valid.
    # </summary>
    BadSequenceNumberInvalid = 0x80880000
    """
    Invalid sequence number.
    """
    # <summary>
    # The applications do not have compatible protocol versions.
    # </summary>
    BadProtocolVersionUnsupported = 0x80BE0000
    """
    Application does not have compatible protocol versions.
    """
    # <summary>
    # There is a problem with the configuration that affects the usefulness of the value.
    # </summary>
    BadConfigurationError = 0x80890000
    """
    Problem with configuration affecting value's usefulness.
    """
    # <summary>
    # The variable should receive its value from another variable, but has never been configured to do so.
    # </summary>
    BadNotConnected = 0x808A0000
    """
    Variable must receive its value from another variable, but it was never configured to do so.
    """
    # <summary>
    # There has been a failure in the device/data source that generates the value that has affected the value.
    # </summary>
    BadDeviceFailure = 0x808B0000
    """
    A failure happened on the device or data source that generates the value and it affected that value.
    """
    # <summary>
    # There has been a failure in the sensor from which the value is derived by the device/data source.
    # </summary>
    BadSensorFailure = 0x808C0000
    """
    A failure happened in the sensor from which the value derives by the device or data source.
    """
    # <summary>
    # The source of the data is not operational.
    # </summary>
    BadOutOfService = 0x808D0000
    """
    Data source is not operational.
    """
    # <summary>
    # The deadband filter is not valid.
    # </summary>
    BadDeadbandFilterInvalid = 0x808E0000
    """
    Invalid dead band filter.
    """
    # <summary>
    # Communication to the data source has failed. The variable value is the last value that had a good quality.
    # </summary>
    UncertainNoCommunicationLastUsableValue = 0x408F0000
    """
    Communication with data source failed. Value of the variable is the last value with a good quality.
    """
    # <summary>
    # Whatever was updating this value has stopped doing so.
    # </summary>
    UncertainLastUsableValue = 0x40900000
    """
    Whatever updating this value stopped doing so.
    """
    # <summary>
    # The value is an operational value that was manually overwritten.
    # </summary>
    UncertainSubstituteValue = 0x40910000
    """
    Value is an operational value manually overwritten.
    """
    # <summary>
    # The value is an initial value for a variable that normally receives its value from another variable.
    # </summary>
    UncertainInitialValue = 0x40920000
    """
    Value is an initial value for a variable that normally receives its value from another variable.
    """
    # <summary>
    # The value is at one of the sensor limits.
    # </summary>
    UncertainSensorNotAccurate = 0x40930000
    """
    Value is at one of sensor limits.
    """
    # <summary>
    # The value is outside of the range of values defined for this parameter.
    # </summary>
    UncertainEngineeringUnitsExceeded = 0x40940000
    """
    Value is outside the range of values defined for this parameter.
    """
    # <summary>
    # The value is derived from multiple sources and has less than the required number of Good sources.
    # </summary>
    UncertainSubNormal = 0x40950000
    """
    Value is derived from multiple sources and contains less than the required number of good sources.
    """
    # <summary>
    # The value has been overridden.
    # </summary>
    GoodLocalOverride = 0x00960000
    """
    Value was overridden
    """
    # <summary>
    # This Condition refresh failed, a Condition refresh operation is already in progress.
    # </summary>
    BadRefreshInProgress = 0x80970000
    """
    Failed refreshing condition because a refresh operation is already in progress.
    """
    # <summary>
    # This condition has already been disabled.
    # </summary>
    BadConditionAlreadyDisabled = 0x80980000
    """
    This condition was already disabled.
    """
    # <summary>
    # This condition has already been enabled.
    # </summary>
    BadConditionAlreadyEnabled = 0x80CC0000
    """
    This condition was already enabled.
    """
    # <summary>
    # Property not available, this condition is disabled.
    # </summary>
    BadConditionDisabled = 0x80990000
    """
    Property not available, this condition is disabled.
    """
    # <summary>
    # The specified event id if not recognized.
    # </summary>
    BadEventIdUnknown = 0x809A0000
    """
    Specified event ID is not recognized.
    """
    # <summary>
    # The event cannot be acknowledged.
    # </summary>
    BadEventNotAcknowledgeable = 0x80BB0000
    """
    Event cannot be acknowledged.
    """
    # <summary>
    # The dialog condition is not active.
    # </summary>
    BadDialogNotActive = 0x80CD0000
    """
    Dialog condition is not active.
    """
    # <summary>
    # The response is not valid for the dialog.
    # </summary>
    BadDialogResponseInvalid = 0x80CE0000
    """
    Response is not valid for the dialog.
    """
    # <summary>
    # The condition branch has already been acknowledged.
    # </summary>
    BadConditionBranchAlreadyAcked = 0x80CF0000
    """
    Condition branch was already acknowledged.
    """
    # <summary>
    # The condition branch has already been confirmed.
    # </summary>
    BadConditionBranchAlreadyConfirmed = 0x80D00000
    """
    Condition branch was already confirmed.
    """
    # <summary>
    # The condition has already been shelved.
    # </summary>
    BadConditionAlreadyShelved = 0x80D10000
    """
    Condition was already shelved.
    """
    # <summary>
    # The condition is not currently shelved.
    # </summary>
    BadConditionNotShelved = 0x80D20000
    """
    Condition is not currently shelved.
    """
    # <summary>
    # The shelving time not within an acceptable range.
    # </summary>
    BadShelvingTimeOutOfRange = 0x80D30000
    """
    Shelving time is not within an acceptable range.
    """
    # <summary>
    # No data exists for the requested time range or event filter.
    # </summary>
    BadNoData = 0x809B0000
    """
    There is no data for the requested time range or event filter.
    """
    # <summary>
    # No data found to provide upper or lower bound value.
    # </summary>
    BadNoBound = 0x809C0000
    """
    There is no data to provide upper or lower bound value.
    """
    # <summary>
    # Data is missing due to collection started/stopped/lost.
    # </summary>
    BadDataLost = 0x809D0000
    """
    Data is missing due to collection started, stopped, or lost.
    """
    # <summary>
    # Expected data is unavailable for the requested time range due to an un-mounted volume, an off-line archive or tape, or similar reason for temporary unavailability.
    # </summary>
    BadDataUnavailable = 0x809E0000
    """
    Expected data is unavailable for the requested time range due to an unmounted volume, an off-line archive or tape, or a similar reason for temporary unavailability.
    """
    # <summary>
    # The data or event was not successfully inserted because a matching entry exists.
    # </summary>
    BadEntryExists = 0x809F0000
    """
    Data or event was not successfully inserted because a matching entry already exists.
    """
    # <summary>
    # The data or event was not successfully updated because no matching entry exists.
    # </summary>
    BadNoEntryExists = 0x80A00000
    """
    Data or event was not successfully updated because no matching entry exists.
    """
    # <summary>
    # The client requested history using a timestamp format the server does not support (i.e requested ServerTimestamp when server only supports SourceTimestamp).
    # </summary>
    BadTimestampNotSupported = 0x80A10000
    """
    Client requested history using a timestamp format not supported by the server, that is, the requested ServerTimestamp only supports SourceTimestamp.
    """
    # <summary>
    # The data or event was successfully inserted in the historical database.
    # </summary>
    GoodEntryInserted = 0x00A20000
    """
    Data or event was successfully inserted in the historical database.
    """
    # <summary>
    # The data or event field was successfully replaced in the historical database.
    # </summary>
    GoodEntryReplaced = 0x00A30000
    """
    Data or event field was successfully replaced in the historical database.
    """
    # <summary>
    # The value is derived from multiple values and has less than the required number of Good values.
    # </summary>
    UncertainDataSubNormal = 0x40A40000
    """
    Value is derived from multiple values and contains less than the required number of good values.
    """
    # <summary>
    # No data exists for the requested time range or event filter.
    # </summary>
    GoodNoData = 0x00A50000
    """
    There is no data for the requested time range or event filter.
    """
    # <summary>
    # The data or event field was successfully replaced in the historical database.
    # </summary>
    GoodMoreData = 0x00A60000
    """
    Data or event field was successfully replaced in the historical database.
    """
    # <summary>
    # The communication layer has raised an event.
    # </summary>
    GoodCommunicationEvent = 0x00A70000
    """
    Communication layer raised an event.
    """
    # <summary>
    # The system is shutting down.
    # </summary>
    GoodShutdownEvent = 0x00A80000
    """
    System is shutting down.
    """
    # <summary>
    # The operation is not finished and needs to be called again.
    # </summary>
    GoodCallAgain = 0x00A90000
    """
    Operation is not finished and must be called again.
    """
    # <summary>
    # A non-critical timeout occurred.
    # </summary>
    GoodNonCriticalTimeout = 0x00AA0000
    """
    A non-critical time-out occurred.
    """
    # <summary>
    # One or more arguments are invalid.
    # </summary>
    BadInvalidArgument = 0x80AB0000
    """
    One or more arguments are invalid.
    """
    # <summary>
    # Could not establish a network connection to remote server.
    # </summary>
    BadConnectionRejected = 0x80AC0000
    """
    Could not establish a network connection to a remote server.
    """
    # <summary>
    # The server has disconnected from the client.
    # </summary>
    BadDisconnect = 0x80AD0000
    """
    Server disconnected from client.
    """
    # <summary>
    # The network connection has been closed.
    # </summary>
    BadConnectionClosed = 0x80AE0000
    """
    Network connection was closed.
    """
    # <summary>
    # The operation cannot be completed because the object is closed, uninitialized or in some other invalid state.
    # </summary>
    BadInvalidState = 0x80AF0000
    """
    Operation cannot be completed because the object is closed, uninitialized, or in some other invalid state.
    """
    # <summary>
    # Cannot move beyond end of the stream.
    # </summary>
    BadEndOfStream = 0x80B00000
    """
    Cannot move beyond the end of the stream.
    """
    # <summary>
    # No data is currently available for reading from a non-blocking stream.
    # </summary>
    BadNoDataAvailable = 0x80B10000
    """
    No data is currently available for reading from a non-blocking stream.
    """
    # <summary>
    # The asynchronous operation is waiting for a response.
    # </summary>
    BadWaitingForResponse = 0x80B20000
    """
    Asynchronous operation is waiting for a response.
    """
    # <summary>
    # The asynchronous operation was abandoned by the caller.
    # </summary>
    BadOperationAbandoned = 0x80B30000
    """
    Asynchronous operation abandoned by the caller.
    """
    # <summary>
    # The stream did not return all data requested (possibly because it is a non-blocking stream).
    # </summary>
    BadExpectedStreamToBlock = 0x80B40000
    """
    Stream did not return all requested data, possibly because it is a non-blocking stream.
    """
    # <summary>
    # Non blocking behaviour is required and the operation would block.
    # </summary>
    BadWouldBlock = 0x80B50000
    """
    Non-blocking behaviour required, therefore the operation will be blocked.
    """
    # <summary>
    # A value had an invalid syntax.
    # </summary>
    BadSyntaxError = 0x80B60000
    """
    Invalid value syntax.
    """
    # <summary>
    # The operation could not be finished because all available connections are in use.
    # </summary>
    BadMaxConnectionsReached = 0x80B70000
    """
    Operation could not be finished because all available connections are in use.
    """
    # <summary>
    # The operation completed successfully.
    # </summary>
    Good = 0x00000000
    """
    Operation completed successfully.
    """
    # <summary>
    # The operation completed however its outputs may not be usable.
    # </summary>
    Uncertain = 0x40000000
    """
    Operation completed, but its outputs may not be usable.
    """
    # <summary>
    # The operation failed.
    # </summary>
    Bad = 0x80000000
    """
    Operation failed.
    """