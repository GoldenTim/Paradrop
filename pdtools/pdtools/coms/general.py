'''
Generic communication tasks. 

All remote calls are inline deferred callbacks. This allows them to be
easily chained together and fired asynchronously. 

Since calls are started with task.react, each method must take a reactor as its 
first parameter. 

Adding the defaultCallbacks decorator prints the result of the operation on 
success or failure. All failed calls return an exception which should be 
suitable for printing. 
'''

from twisted.internet import defer

from pdtools.coms.client import RpcClient
from pdtools.lib.output import out
from pdtools.lib import pdutils
from pdtools.lib import store
from pdtools.lib import riffle

# SERVER_HOST = 'paradrop.io'
SERVER_HOST = 'localhost'
SERVER_PORT = 8015
SERVER_RIFFLE_PORT = 8016

###############################################################################
# Default Callbacks
###############################################################################


def failureCallbacks(f):
    def w(*args, **kwargs):
        return f(*args, **kwargs).addErrback(printFailure)

    return w


def defaultCallbacks(f):
    ''' 
    Wrap the API call in default handlers which print results. Optional 
    params are used to turn off specific handlers
    '''
    def w(*args, **kwargs):
        return f(*args, **kwargs).addCallbacks(printSuccess, printFailure)

    return w


def printSuccess(r):
    if isinstance(r, list):
        for x in r:
            print x
    else:
        print r


def printFailure(r):
    print 'Operation Failed!'
    print r


###############################################################################
# Generic Functionality
###############################################################################

@defaultCallbacks
@defer.inlineCallbacks
def logs(reactor, host, port):
    ''' Connect to the named device and ask for logs. '''
    client = RpcClient(host, port, 'internal')
    res = yield client.log()

    # comes back raw from the file, have to convert back to dics
    # converted = [pdutils.str2json(x) for x in res.strip().split('\n')]
    # for a in [out.messageToString(x) for x in converted]:
    #     print a

    # Cant do this more succintly until we find the encoding bugs
    for x in res.strip().split('\n'):
        try:
            j = pdutils.str2json(x)
            s = out.messageToString(j)
            print s
        except:
            print 'Malformed line, raw output: ' + x

    defer.returnValue('Done')


class ServerPerspective(riffle.RifflePerspective):

    def perspective_echo(self, arg):
        print 'Client: server called echo'
        return arg


@defaultCallbacks
@defer.inlineCallbacks
def echo(reactor, host, port):
    capath = '/home/damouse/Documents/python/scratch/oldkeys/ca-private-cert.pem'
    keypath = '/home/damouse/Documents/python/scratch/oldkeys/b.client.private.pem'

    # caPem, pem = store.store.getKey('ca.pem'), store.store.getKey('client.pem')
    with open(capath, 'r') as f:
        ca = f.read()

    with open(keypath, 'r') as f:
        key = f.read()

    # ca, key = ca.strip(), key.strip()

    #Testing...
    riffle.portal.addRealm(u'the-authority', riffle.Realm(ServerPerspective))

    avatar = yield riffle.Riffle(host, int(port)).connect(ca, key)
    result = yield avatar.echo('Hello from a client!')
    defer.returnValue(result)


###############################################################################
# Riffle Convenience Methods
###############################################################################

def connectServer():
    ''' Quick refactor method, returns a riffle client ready to communicate with the server '''
    return riffle.Riffle('localhost', 4322).connect(store.KEY_PATH)
