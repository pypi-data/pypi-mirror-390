from TestHelperSuperClass import testHelperSuperClass, env
from baseapp_for_restapi_backend_with_swagger import apiSecurityCheck, DecodedTokenClass
import jwt
from base64 import b64decode, b64encode
import datetime
import pytz
from unittest.mock import patch

from werkzeug.exceptions import Unauthorized, Forbidden

jwtSecret=b64encode('asasadfrg4tgtsferegfdwqefsrgfsdfdsffds'.encode("utf-8"))
jwtSecret2=b64encode('asdsdsda'.encode("utf-8"))
tenant='someTenant'

class getClass():
  data = None
  curKey = -1
  keyList = None
  def __init__(self, data):
    self.data = {}
    for x in data:
      self.data[x] = data[x]

    self.data = data
  def get(self, key):
    return self.data[key]

  def __iter__(self):
    self.curKey = 0
    self.keyList = []
    for x in self.data:
      self.keyList.append(x)
    return self

  def __next__(self):
    if self.curKey >= len(self.data.keys()):
      raise StopIteration
    else:
      self.curKey += 1
      return self.keyList[self.curKey - 1]

class mockRequestObjectClass():
  headers = None
  cookies = None
  def __init__(self, headers, cookies):
    self.headers = getClass(headers)

class CurTime():
  frozen=None
  def get(self):
    if self.frozen is None:
      return datetime.datetime.now(pytz.timezone("UTC"))
    return self.frozen
  def freeze(self, timeToFreezeAt):
    self.frozen = timeToFreezeAt
  def unfreeze(self):
    self.frozen = None
curTime=CurTime()

def generateToken(secret, roleListForTenant=[]):
  expiryTime = curTime.get() + datetime.timedelta(seconds=int(5)) #5 second expiry

  JWTDict = {}
  JWTDict['authedPersonGuid'] = 'personGUID'
  JWTDict['iss'] = 'key'
  JWTDict['exp'] = expiryTime
  JWTDict['TenantRoles'] = {
    tenant: roleListForTenant
  }

  encodedJWT = jwt.encode(JWTDict, b64decode(secret), algorithm='HS256')
  return encodedJWT


class test_apiSecurity(testHelperSuperClass):
  def setUp(self):
    curTime.unfreeze()

  def test_userWithNoTokenAtAllIsRefused(self):
    request = mockRequestObjectClass({}, {})

    with self.assertRaises(Exception) as context:
      decodedToken = apiSecurityCheck(request, tenant, [], [], [], jwtSecret)
    self.checkGotRightExceptionType(context,Unauthorized)

  def test_sendInNonTokenHeader(self):
    headers = {'aa':'somestring'}
    request = mockRequestObjectClass(headers, {})

    with self.assertRaises(Exception) as context:
      decodedToken = apiSecurityCheck(request, tenant, [], ['aa'], [], jwtSecret)
    self.checkGotRightExceptionType(context,Unauthorized)

  def test_workingJWTTokenInHeader(self):
    token = generateToken(jwtSecret)

    headers = {'aa':token}
    request = mockRequestObjectClass(headers, {})

    decodedToken = apiSecurityCheck(request, tenant, [], ['aa'], [], jwtSecret)

  def test_workingJWTTokenInHeaderMissingRole(self):
    token = generateToken(jwtSecret)
    d = DecodedTokenClass(jwtSecret, token)

    headers = {'aa':token}
    request = mockRequestObjectClass(headers, {})

    with self.assertRaises(Exception) as context:
      decodedToken = apiSecurityCheck(request, tenant, ['someRoleWeWant'], ['aa'], [], jwtSecret)
    self.checkGotRightExceptionType(context,Forbidden)

  def test_workingJWTTokenInGotRole(self):
    token = generateToken(jwtSecret,'someRoleWeWant')

    headers = {'aa':token}
    request = mockRequestObjectClass(headers, {})

    decodedToken = apiSecurityCheck(request, tenant, ['someRoleWeWant'], ['aa'], [], jwtSecret)

  def test_workingJWTTokenInGotRoleButNotSearchingThatHeader(self):
    token = generateToken(jwtSecret,'someRoleWeWant')

    headers = {'aa':token}
    request = mockRequestObjectClass(headers, {})

    with self.assertRaises(Exception) as context:
      decodedToken = apiSecurityCheck(request, tenant, ['someRoleWeWant'], ['bb'], [], jwtSecret)
    self.checkGotRightExceptionType(context,Unauthorized)

  def test_JWTTokenIsInAuthorizationHeader(self):
    token = generateToken(jwtSecret,'someRoleWeWant')

    headers = {'Authorization': 'Bearer ' + token}
    request = mockRequestObjectClass(headers, {})

    decodedToken = apiSecurityCheck(request, tenant, ['someRoleWeWant'], [], [], jwtSecret)

  #reviewing this test I don't know what should happen. I get invalid signature error but I think I should
  #  it's an invalid case anyway. If I have different tokens in header and aa header then I don't know
  def test_differentJWTTokenIsInAuthorizationHeaderRightTokenInAAHeader(self):
    token = generateToken(jwtSecret,'someRoleWeWant')
    token2 = generateToken(jwtSecret2,'someRoleWeWant')

    headers = {'Authorization': 'Bearer ' + token2}
    headers['aa'] = token
    request = mockRequestObjectClass(headers, {})

    with self.assertRaises(Exception) as context:
      decodedToken = apiSecurityCheck(request, tenant, ['someRoleWeWant'], ['aa'], [], jwtSecret)

  def test_callSecurityWithInvalidToken(self):
    token = 'Someinvlaidnonbase64String'
    headersToSearch = ['cddc']
    headers = {'cddc': token}
    request = mockRequestObjectClass(headers, {})

    with self.assertRaises(Exception) as context:
      decodedToken = apiSecurityCheck(request, tenant, [], headersToSearch, [], jwtSecret)
    self.checkGotRightExceptionType(context,Unauthorized)
    self.assertEqual(str(context.exception),'401 Unauthorized: Problem with token',msg="Wrong error message returned")

  def test_invalidJWTTokenSignatureFails(self):
    token = generateToken(jwtSecret2)

    headers = {'aa':token}
    request = mockRequestObjectClass(headers, {})

    with self.assertRaises(Exception) as context:
      decodedToken = apiSecurityCheck(request, tenant, [], ['aa'], [], jwtSecret)
    self.checkGotRightExceptionType(context,Unauthorized)
    self.assertEqual(str(context.exception),'401 Unauthorized: InvalidSignatureError',msg="Wrong error message returned")

  def test_invalidJWTTokenSignatureSkipMakesItWork(self):
    token = generateToken(jwtSecret2)

    headers = {'aa':token}
    request = mockRequestObjectClass(headers, {})

    decodedToken = apiSecurityCheck(request, tenant, [], ['aa'], [], jwtSecret, skipSignatureValidation=True)

  def test_tokenExpiry(self):
    curTime.freeze(datetime.datetime.now(pytz.timezone("UTC")) - datetime.timedelta(seconds=int(50)))
    token = generateToken(jwtSecret)

    headers = {'aa':token}
    request = mockRequestObjectClass(headers, {})

    with self.assertRaises(Exception) as context:
      decodedToken = apiSecurityCheck(request, tenant, [], ['aa'], [], jwtSecret)
    self.checkGotRightExceptionType(context,Unauthorized)
    self.assertEqual(str(context.exception),"401 Unauthorized: ExpiredSignatureError")
