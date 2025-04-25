# 1. Discord Listener
## 1.1. receive messages
### 1.1.1 direct messages
#### Test 1 - ping
send message to bot 
e.g. `@imposter fdgas`
Expect:
handle private message - `fdgas` should be found in logs

#### Test 2 - no ping
send private message to bot without ping
e.g. `dfsadfgs sgdfhs`
Expect 
handle private message - `dfsadfgs sgdfhs` should be found in logs

### 1.1.2 Group messages (not implemented but can we add bot to group?)
#### Test 1 - ping
send message to bot 
e.g. `@imposter fdgas`
Expect:
handle private message - `fdgas` should be found in logs

#### Test 2 - no ping
send private message to bot without ping
e.g. `dfsadfgs sgdfhs`
Expect 
**DO NOT** handle private message - `dfsadfgs sgdfhs` should **not** be found in logs

### 1.1.3 channel messages
#### Test 1 - ping
send message to bot 
e.g. `@imposter fdgas`
Expect:
handle private message - `fdgas` should be found in logs

#### Test 2 - no ping
send private message to bot without ping
e.g. `dfsadfgs sgdfhs`
Expect: 
**DO NOT** handle private message - `dfsadfgs sgdfhs` should **not** be found in logs

#### Test 3 - multiple ping
pings multiple user with imposter included (imposter should not be the first)
e.g. `@pigu @imposter abcdefg`
Expect:
idk?

## 1.2. Delete message
### Test 1 - Guild chat 
Successful process
Expect:
deletes message

### Test 2 - Guild chat (fail)
Failed process
Expect:
message fail

### Test 3 - private message
Successful process
Expect:
**DO NOT** delete message

