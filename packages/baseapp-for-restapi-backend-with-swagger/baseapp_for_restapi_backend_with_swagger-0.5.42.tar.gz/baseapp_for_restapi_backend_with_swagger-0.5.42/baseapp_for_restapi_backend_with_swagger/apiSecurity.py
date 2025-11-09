from werkzeug.exceptions import Unauthorized, Forbidden, BadRequest, InternalServerError, NotFound, Conflict
import jwt
from base64 import b64decode

#Test to see if caller is allowed access to this API

def _getFromHeader(request, headers):
  for h in headers:
    if h in request.headers:
      token = request.headers.get(h)
      return token
  return None

def _getFromLoginCookie(request, cookies):
  for c in cookies:
    if c in request.cookies:
      cookie = request.cookies.get(c)
      try:
        a = unquote(cookie)
        a = json.loads(a)
        if 'jwtData' in a.keys():
          if 'JWTToken' in a['jwtData']:
            return a['jwtData']['JWTToken']
      except:
        pass
  return None

def getTokenFromAuthorizationHeader(request, jwtSecret):
  if 'Authorization' not in request.headers:
    return None
  a = request.headers.get('Authorization')
  if not a.startswith('Bearer '):
    return None
  a = a[7:].strip()
  return a


def _getFromNormCookie(request, cookies):
  for c in cookies:
    if c in request.cookies:
      return request.cookies.get(c)

#This will ALWAYS search the Authorization: Bearer header
def apiSecurityCheck(request, tenant, requiredRoleList, headersToSearch, cookiesToSearch, jwtSecret, skipSignatureValidation=False, outputExceptions=False, getCurDateTime=None):
  jwtToken = getTokenFromAuthorizationHeader(request, jwtSecret)
  if jwtToken is None:
    jwtToken = _getFromHeader(request, headersToSearch)
    if jwtToken is None:
      jwtToken = _getFromLoginCookie(request, cookiesToSearch)
      if jwtToken is None:
        jwtToken = _getFromNormCookie(request, cookiesToSearch)
        if jwtToken is None:
          raise Unauthorized("No JWT Token in header or cookie")

  if jwtSecret is None:
    raise Unauthorized('Unable to verify JWT token as APIAPP_JWTSECRET is not set (Precheck)')


  try:
    decodedJWTToken = DecodedTokenClass(jwtSecret, jwtToken, (not skipSignatureValidation), getCurDateTime=getCurDateTime)
  except jwt.InvalidSignatureError:
    raise Unauthorized("InvalidSignatureError")
  except jwt.ExpiredSignatureError:
    raise Unauthorized("ExpiredSignatureError")
  except Exception as err:
    if outputExceptions:
      print("EXCEPTION decoding JWT token:")
      print(err) # for the repr
      print(str(err)) # for just the message
      print(err.args) # the arguments that the exception has been called with.
    raise Unauthorized("Problem with token")

  for x in requiredRoleList:
    if not decodedJWTToken.hasRole(tenant, x):
      raise Forbidden("Missing required Role")

  return decodedJWTToken

def decodeJWTToken(token, secret, verify):
  if verify:
    return jwt.decode(token, b64decode(secret), algorithms=['HS256'])
  options = {
    "verify_signature": False
  }
  return jwt.decode(token, options=options, algorithms=['HS256'])


class DecodedTokenClass():
  _tokenData = None
  origJWTToken = None

  def __init__(self, jwtSecret, jwttoken, verify=True, getCurDateTime=None):
    if jwtSecret is None:
      raise Exception('Unable to verify JWT token as APIAPP_JWTSECRET is not set')

    self.origJWTToken = jwttoken

    #Does two decodes, one without verification
    ## this means we can read the userID
    UserID = decodeJWTToken(jwttoken, None, False)['iss']
    self._tokenData = decodeJWTToken(jwttoken, jwtSecret, verify)

    #pyJWT does this for us but sometimes we test with a different internal clock
    if getCurDateTime is not None:
      if (getCurDateTime().timestamp() > self._tokenData["exp"]):
        raise jwt.ExpiredSignatureError()

  def hasRole(self, tenant, role):
    if tenant not in self._tokenData['TenantRoles']:
      return False
    if role not in self._tokenData['TenantRoles'][tenant]:
      return False
    return True

  def getUserID(self):
    return self._tokenData["UserID"]

  def getPersonID(self):
    return self._tokenData["authedPersonGuid"]

  def getOrigJWTToken(self):
    return self.origJWTToken
