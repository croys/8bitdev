from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest


@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/src/a1replica.p')
    return M

####################################################################
#   Utility routines

@pytest.mark.parametrize('x, cycles', (
    (0x01,     23), # "no" delay: 23 μs
    (0x02,   1819), # minimum real delay: 1.8 ms
    (0x03,   3615), # next step: 3.6 ms; each additional step adds about 1.8 ms
   #(0x81, 229911), # half total delay available: about 230 ms (slowish test)
))
def test_humdly(M, x, cycles):
    M.call(M.symtab.loopdly, R(x=x))
    assert cycles == M.mpu.processorCycles  # test framework doesn't include RTS

@pytest.mark.skip(reason='Slow test')
def test_humdlymax(M):
    M.call(M.symtab.loopdlymax, R(x=3), maxops=1000000000)
    assert 457987 == M.mpu.processorCycles  # about half a second at 1 MHz

####################################################################
#   PIA routines

def test_countup(M):
    S = M.symtab

    #   NOP out the delay call
    jsrloc = S.countup + 0x0B
    assert [I.JSR, S.loopdly & 0xFF, S.loopdly >> 8] == M.bytes(jsrloc, 3)
    M.deposit(jsrloc, [I.NOP]*3)

    #   One way to debug this would be to stop every time we hit the
    #   following symbol, but the test framework currently doesn't
    #   support that.
    loop = S.sym('countup.loop')    # could stop here....
    M.call(S.countup, stopsat=[loop])
