# Generated from c:\sms3a.tlb

from ctcom import IUnknown, GUID, COMPointer
from ctcom.typeinfo import IDispatch, BSTR

from ctypes import POINTER, c_voidp, c_byte, c_ubyte, \
     c_short, c_ushort, c_int, c_uint, c_long, c_ulong, \
     c_float, c_double

class COMObject:
    pass

class enum(c_int):
    pass


##############################################################################

class STORAGE_STATUS(enum):
    """SMS storage status type"""
    _iid_ = GUID('{1577C341-174C-11D3-B1FF-006097838405}')
    NOT_SENT_FROM_PHONE = 0
    SENT_FROM_PHONE = 1
    DELIVERED = 2
    READ_FROM_PHONE = 3
    NOT_READ_FROM_PHONE = 4


class USER_DATA_FORMAT(enum):
    """SMS user data coding format"""
    _iid_ = GUID('{475AF0E3-14FD-11D3-B1FF-006097838405}')
    DATA_CODING_SCHEME_BASED = 0
    DEFAULT_ALPHABET_7_BIT = 1
    DATA_8_BIT = 2
    UNICODE_16_BIT = 3


class VALIDITY_PERIOD_FORMAT(enum):
    """SMS validity period type"""
    _iid_ = GUID('{F1D64502-176A-11D3-B1FF-006097838405}')
    NOT_PRESENT = 0
    RELATIVE_FORMAT = 1
    ENHANCED_FORMAT = 2
    ABSOLUTE_FORMAT = 3


class SMS_MEMORY_LOCATION(enum):
    """SMS memory location type"""
    _iid_ = GUID('{1577C343-174C-11D3-B1FF-006097838405}')
    SIM_MEMORY = 0
    PHONE_MEMORY = 1
    DEFAULT_MEMORY = 2


class REPORT_QUALIFIER(enum):
    """Type of message that has requested Status Report"""
    _iid_ = GUID('{475AF0E4-14FD-11D3-B1FF-006097838405}')
    SUBMIT_REQUESTED = 0
    COMMAND_REQUESTED = 1


class SMS_MESSAGE_TYPE(enum):
    """SMS message type"""
    _iid_ = GUID('{475AF0E5-14FD-11D3-B1FF-006097838405}')
    DELIVER_MESSAGE = 0
    STATUS_REPORT_MESSAGE = 1
    SUBMIT_MESSAGE = 2
    COMMAND_MESSAGE = 3
    MO_UNDEFINED_MESSAGE = 4
    MT_UNDEFINED_MESSAGE = 5


class NmpAdapterError(enum):
    """Nokia adapter error codes"""
    _iid_ = GUID('{60CC5E00-D3A2-11D1-99A0-0060979AC1B6}')
    errCalendarNotSupported = 5377
    errCalendarUnknownNoteType = 5378
    errCalendarUnknownItemType = 5379
    errCalendarComponentCreation = 5380
    errCalendarItemRead = 5381
    errCalendarItemWrite = 5382
    errCalendarItemDelete = 5383
    errCalendarCallEmpty = 5384
    errCalendarNoMoreNotes = 5385
    errCalendarEmpty = 5386
    errCalendarNoDelete = 5387
    errCallNoActiveCall = 5633
    errCallNoDualModeCall = 5634
    errCallAlreadyActive = 5635
    errCallSignallingFailure = 5636
    errCallInvalidMode = 5637
    errCbSettingSetFailed = 5889
    errCbInvalidLanguage = 5890
    errCbInvalidTopic = 5891
    errCbToomanyLang = 5892
    errCbToomanyTopic = 5893
    errPnInvalidMemory = 6145
    errPnNumberTooLong = 6146
    errPnNameTooLong = 6147
    errPnInvalidCharacters = 6148
    errPnMemoryFull = 6149
    errPnNotAvail = 6150
    errPnTimestampNotavail = 6151
    errPnCallergroupsNotsupported = 6152
    errPnInvalidIconFormat = 6153
    errPnEntryLocked = 6154
    errPnSpeedkeyNotassigned = 6155
    errPnEmpty = 6156
    errDataNotAvail = 6401
    errSsUnknownSubscriber = 6402
    errSsBearerServNotProvision = 6403
    errSsTeleServNotProvision = 6404
    errSsCUGReject = 6405
    errSsIllegalSsOperation = 6406
    errSsErrorStatus = 6407
    errSsNotAvailable = 6408
    errSsSubscriptionViolation = 6409
    errSsIncompatibility = 6410
    errSsSpecificError = 6411
    errSsSystemFailure = 6412
    errSsDataMissing = 6413
    errSsUnexpectedDataValue = 6414
    errSsPasswordRegisFailure = 6415
    errSsNegativePasswordCheck = 6416
    errSsFacilityNotSupported = 6417
    errSsResourcesNotAvailable = 6418
    errSsMaxnumOfMptyPartExceed = 6419
    errSsCallBarred = 6420
    errSsMaxnumOfPwAttViolation = 6421
    errSsAbsentSubscriber = 6422
    errSsUSSDBusy = 6423
    errSsUnknownAlphabet = 6424
    errWrongPassword = 6425
    errPasswordNotRequired = 6426
    errUpdateImpossible = 6427
    errNetCallActive = 6428
    errNetNoMsgToQuit = 6429
    errNetUnableToQuit = 6430
    errNetAccessDenied = 6431
    errSsMMError = 6432
    errSsMsgError = 6433
    errSsMMRelease = 6434
    errSsActivationDataLost = 6435
    errSsServiceBusy = 6436
    errSsDataError = 6437
    errSsTimerExpired = 6438
    errSsPWErrorEnterPassword = 6439
    errSsPWErrorEnterNewPassword = 6440
    errSsPWErrorEnterNewPasswordAgain = 6441
    errSsPWErrorBadPassword = 6442
    errSsPWErrorBadPasswordFormat = 6443
    errSsPReturnErrorProblem = 6444
    errSsPUnrecognizedComp = 6445
    errSsPMistypedComp = 6446
    errSsPBadlyStructuredComp = 6447
    errSsPDuplicateInvokeID = 6448
    errSsPUnrecognizedOperation = 6449
    errSsPMistypedInvParameter = 6450
    errSsPResourceLimitation = 6451
    errSsPInitiatingRelease = 6452
    errSsPUnrecognizedLinkedID = 6453
    errSsPLinkedRespUnexpected = 6454
    errSsPUnexpectedLinkedOper = 6455
    errSsPUnrecognizedInvokeID = 6456
    errSsPReturnResultUnexpected = 6457
    errSsPMistypedResParameter = 6458
    errSsPReturnErrorUnexpected = 6459
    errSsPUnrecognizedError = 6460
    errSsPUnexpectedError = 6461
    errSsPMistypedErrParameter = 6462
    errSmsCreateFailed = 6657
    errSmsCannotSendMTMessages = 6658
    errSmsInvalidType = 6659
    errSmsInvalidDataCodingScheme = 6660
    errSmsInvalidUserDataLength = 6661
    errSmsInvalidUserDataFormat = 6662
    errSmsInvalidUserData = 6663
    errSmsInvalidUserDataHeaderLength = 6664
    errSmsInvalidSCTimeStamp = 6665
    errSmsTooLongSCAddress = 6666
    errSmsInvalidValidityPeriod = 6667
    errSmsTooLongOtherEndAddress = 6668
    errSmsInvalidParameterSetIndex = 6669
    errSmsTypeMOUndefined = 6670
    errSmsTypeMTUndefined = 6671
    errSmsTypeCommand = 6672
    errSmsNoSCAddress = 6673
    errSmsDefaultSetNameUsed = 6674
    errProtocolError = 6675
    errBookmarkEmpty = 7169
    errGroupEmpty = 7170
    errNoError = 0
    errUnknown = 7935
    errInvalidLocation = 7681
    errInvalidParameter = 7682
    errReserved = 7683
    errMemoryFull = 7684
    errEmptyLocation = 7685
    errInvalidNumber = 7686
    errCallCostLimitReached = 7687
    errRLP = 7688
    errCommunicationError = 7689
    errNotSupported = 7690
    errMpApiNotAvail = 7691
    errDeviceFailure = 7692
    errNoSim = 7693
    errTerminalNotReady = 7694
    errSignallingFailure = 7695
    errPhoneNotConnected = 7696
    errPinRequired = 7697
    errPukRequired = 7698
    errPin2Required = 7699
    errPuk2Required = 7700
    errSecurityCodeRequired = 7701
    errBarred = 7702
    errSIMRejected = 7703


##############################################################################

class ISMSSend(IUnknown):
    """ISMSSend Interface"""
    _iid_ = GUID('{3369A2C4-E58F-11D1-B1FC-006097838405}')

class ISMSSendPointer(COMPointer):
    _interface_ = ISMSSend

class IShortMessage(IUnknown):
    """IShortMessage Interface"""
    _iid_ = GUID('{3369A2C5-E58F-11D1-B1FC-006097838405}')

class IShortMessagePointer(COMPointer):
    _interface_ = IShortMessage

class ISMSSettings(IUnknown):
    """ISMSSettings Interface"""
    _iid_ = GUID('{0EC2D402-E8BC-11D1-B1FC-006097838405}')

class ISMSSettingsPointer(COMPointer):
    _interface_ = ISMSSettings

class IGMSPicture(IUnknown):
    """IGMSPicture Interface"""
    _iid_ = GUID('{A6DA8A41-354A-49CF-9253-5DC814664A32}')

class IGMSPicturePointer(COMPointer):
    _interface_ = IGMSPicture

class ISMSMemory(IUnknown):
    """ISMSMemory Interface"""
    _iid_ = GUID('{0EC2D401-E8BC-11D1-B1FC-006097838405}')

class ISMSMemoryPointer(COMPointer):
    _interface_ = ISMSMemory

class ISMSReceiveNotify(IUnknown):
    """ISMSReceiveNotify Interface"""
    _iid_ = GUID('{0EC2D403-E8BC-11D1-B1FC-006097838405}')

class ISMSReceiveNotifyPointer(COMPointer):
    _interface_ = ISMSReceiveNotify

class IGraphicalMS(IUnknown):
    """IGraphicalMS Interface"""
    _iid_ = GUID('{8829E754-FA43-4D8D-B009-DB4024BE200E}')

class IGraphicalMSPointer(COMPointer):
    _interface_ = IGraphicalMS

ISMSSend._methods_ = [
    ("CreateShortMsg", [POINTER(POINTER(IShortMessage))]),
    ("Send", [POINTER(IShortMessage)]),
    ("GetLastError", [POINTER(NmpAdapterError)]),
    ("Terminate", []),
    ("StartListeningEvents", []),
]

IShortMessage._methods_ = [
    ("_get_ValidityPeriodFormat", [POINTER(VALIDITY_PERIOD_FORMAT)]),
    ("_put_ValidityPeriodFormat", [VALIDITY_PERIOD_FORMAT]),
    ("_get_ValidityPeriodRelative", [POINTER(c_ubyte)]),
    ("_put_ValidityPeriodRelative", [c_ubyte]),
    ("put_ValidityPeriodAbsolute", [c_long, c_long, c_long, c_long, c_long, c_long, c_long]),
    ("get_ValidityPeriodAbsolute", [POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long)]),
    ("put_ValidityPeriodEnhanced", [c_ubyte, c_ubyte, c_ubyte, c_ubyte, c_ubyte, c_ubyte, c_ubyte]),
    ("get_ValidityPeriodEnhanced", [POINTER(c_ubyte), POINTER(c_ubyte), POINTER(c_ubyte), POINTER(c_ubyte), POINTER(c_ubyte), POINTER(c_ubyte), POINTER(c_ubyte)]),
    ("_get_DataCodingScheme", [POINTER(c_ubyte)]),
    ("_put_DataCodingScheme", [c_ubyte]),
    ("_get_OtherEndAddress", [POINTER(BSTR)]),
    ("_put_OtherEndAddress", [BSTR]),
    ("_get_ProtocolIdentifier", [POINTER(c_ubyte)]),
    ("_put_ProtocolIdentifier", [c_ubyte]),
    ("_get_SCAddress", [POINTER(BSTR)]),
    ("_put_SCAddress", [BSTR]),
    ("get_SCTimeStamp", [POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long)]),
    ("put_SCTimeStamp", [c_long, c_long, c_long, c_long, c_long, c_long, c_long]),
    ("_get_StorageStatus", [POINTER(STORAGE_STATUS)]),
    ("_put_StorageStatus", [STORAGE_STATUS]),
    ("_get_MessageType", [POINTER(SMS_MESSAGE_TYPE)]),
    ("_put_MessageType", [SMS_MESSAGE_TYPE]),
    ("_get_UserDataFormat", [POINTER(USER_DATA_FORMAT)]),
    ("_put_UserDataFormat", [USER_DATA_FORMAT]),
    ("_get_UserDataText", [POINTER(BSTR)]),
    ("_put_UserDataText", [BSTR]),
    ("_get_UserData", [c_long, POINTER(c_ubyte)]),
    ("_put_UserData", [c_long, c_ubyte]),
    ("_get_UserDataHeader", [c_long, POINTER(c_ubyte)]),
    ("_put_UserDataHeader", [c_long, c_ubyte]),
    ("_get_MessageReference", [POINTER(c_ubyte)]),
    ("_put_MessageReference", [c_ubyte]),
    ("_get_StatusReportRequest", [POINTER(c_long)]),
    ("_put_StatusReportRequest", [c_long]),
    ("_get_ReplyPath", [POINTER(c_long)]),
    ("_put_ReplyPath", [c_long]),
    ("_get_CommandType", [POINTER(c_ubyte)]),
    ("_put_CommandType", [c_ubyte]),
    ("_get_CommandMessageNumber", [POINTER(c_ubyte)]),
    ("_put_CommandMessageNumber", [c_ubyte]),
    ("_get_StatusReportQualifier", [POINTER(REPORT_QUALIFIER)]),
    ("_put_StatusReportQualifier", [REPORT_QUALIFIER]),
    ("_get_Status", [POINTER(c_ubyte)]),
    ("_put_Status", [c_ubyte]),
    ("_get_UserDataLength", [POINTER(c_long)]),
    ("_put_UserDataLength", [c_long]),
    ("_get_UserDataHeaderLength", [POINTER(c_long)]),
    ("_put_UserDataHeaderLength", [c_long]),
]

ISMSSettings._methods_ = [
    ("GetCommonSMSSettings", [POINTER(c_long), POINTER(c_long)]),
    ("SetCommonSMSSettings", [c_long, c_long]),
    ("GetSMSParametersSet", [c_long, POINTER(BSTR), POINTER(c_ubyte), POINTER(c_ubyte), POINTER(c_ubyte), POINTER(BSTR)]),
    ("SetSMSParametersSet", [c_long, BSTR, c_ubyte, c_ubyte, c_ubyte, BSTR]),
    ("SetRoutingParameters", [c_ubyte, c_ubyte, c_ubyte, c_ubyte, c_ubyte]),
    ("GetLastError", [POINTER(NmpAdapterError)]),
    ("Terminate", []),
    ("StartListeningEvents", []),
]

IGMSPicture._methods_ = [
    ("_get_MsgRejectDublicates", [POINTER(c_int)]),
    ("_put_MsgRejectDublicates", [c_int]),
    ("_get_MsgReplyPath", [POINTER(c_int)]),
    ("_put_MsgReplyPath", [c_int]),
    ("_get_MsgStatusReportRequest", [POINTER(c_int)]),
    ("_put_MsgStatusReportRequest", [c_int]),
    ("_get_MsgOriginatorAddress", [POINTER(BSTR)]),
    ("_put_MsgOriginatorAddress", [BSTR]),
    ("_get_MsgProtocolID", [POINTER(c_short)]),
    ("_put_MsgProtocolID", [c_short]),
    ("_get_MsgDCS", [POINTER(c_short)]),
    ("_put_MsgDCS", [c_short]),
    ("_get_MsgValidityPeriodFormat", [POINTER(VALIDITY_PERIOD_FORMAT)]),
    ("_put_MsgValidityPeriodFormat", [VALIDITY_PERIOD_FORMAT]),
    ("_get_MsgValidityPeriod", [POINTER(BSTR)]),
    ("_put_MsgValidityPeriod", [BSTR]),
    ("_get_MsgText", [POINTER(BSTR)]),
    ("_put_MsgText", [BSTR]),
    ("_get_PicInfoField", [POINTER(c_short)]),
    ("_put_PicInfoField", [c_short]),
    ("_get_PicDepth", [POINTER(c_short)]),
    ("_put_PicDepth", [c_short]),
    ("_get_PicWidth", [POINTER(c_short)]),
    ("_put_PicWidth", [c_short]),
    ("_get_PicHeight", [POINTER(c_short)]),
    ("_put_PicHeight", [c_short]),
    ("_get_PicDataLength", [POINTER(c_short)]),
    ("_put_PicDataLength", [c_short]),
    ("_get_PicData", [c_short, POINTER(c_short)]),
    ("_put_PicData", [c_short, c_short]),
]

ISMSMemory._methods_ = [
    ("CreateShortMsg", [POINTER(POINTER(IShortMessage))]),
    ("Delete", [SMS_MEMORY_LOCATION, c_long]),
    ("Read", [SMS_MEMORY_LOCATION, c_long, POINTER(POINTER(IShortMessage)), c_long]),
    ("Store", [SMS_MEMORY_LOCATION, c_long, POINTER(IShortMessage)]),
    ("GetCapasityInME", [POINTER(c_long)]),
    ("GetCapasityInSIM", [POINTER(c_long)]),
    ("GetNumberOfMessagesInME", [POINTER(c_long)]),
    ("GetNumberOfMessagesInSIM", [POINTER(c_long)]),
    ("GetNumberOfUnreadInME", [POINTER(c_long)]),
    ("GetNumberOfUnreadInSIM", [POINTER(c_long)]),
    ("GetMemoryConfiguration", [POINTER(c_long)]),
    ("GetCapasityOfParamSets", [POINTER(c_long)]),
    ("GetSMSMemoryStatus", [POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long)]),
    ("GetLastError", [POINTER(NmpAdapterError)]),
    ("Terminate", []),
    ("StartListeningEvents", []),
]

ISMSReceiveNotify._methods_ = [
    ("ShortMsgReceived", [SMS_MEMORY_LOCATION, c_long, POINTER(IShortMessage)]),
    ("SMSMemoryFull", [SMS_MEMORY_LOCATION]),
    ("ShortMsgSent", [POINTER(IShortMessage)]),
]

IGraphicalMS._methods_ = [
    ("CreateGMSObject", [POINTER(POINTER(IGMSPicture))]),
    ("FindNextGMS", [c_int, POINTER(STORAGE_STATUS), POINTER(c_short), POINTER(POINTER(IGMSPicture))]),
    ("SaveGMS", [STORAGE_STATUS, POINTER(IGMSPicture), POINTER(c_short)]),
]

##############################################################################

class GMSPicture(COMObject):
    """Nokia GMSPicture"""
    _regclsid_ = '{FE4A3D7F-DED7-47E9-9F97-4A9859B728B9}'
    _com_interfaces_ = [IGMSPicture]


class ShortMessage(COMObject):
    """Nokia ShortMessage Data Component"""
    _regclsid_ = '{3369A2C6-E58F-11D1-B1FC-006097838405}'
    _com_interfaces_ = [IShortMessage]


class SMS_SuiteAdapter(COMObject):
    """Nokia SMS"""
    _regclsid_ = '{2E6EB774-804D-11D1-B1FC-006097838405}'
    _com_interfaces_ = [ISMSSend, ISMSMemory, ISMSSettings, IGraphicalMS]
    _outgoing_interfaces_ = [ISMSReceiveNotify]

