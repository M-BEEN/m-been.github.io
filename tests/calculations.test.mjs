import test from 'node:test';
import assert from 'node:assert/strict';
import { compound, recovery, costs, position } from '../assets/js/calculations.js';
const near = (a, b, eps = 1e-7) => assert.ok(Math.abs(a-b)<eps, `${a} != ${b}`);
test('asymmetric returns and recovery use the changing denominator', () => {
  const r = compound(10000, [-10, 10]);
  near(r.final, 9900); near(r.total, -1); near(r.arithmetic, 0);
  near(r.geometric, -0.5012562893380035); near(recovery(20), 25); near(recovery(50), 100);
});
test('gains compound and complete loss cannot recover without a cash injection', () => {
  near(compound(100, [10, 10]).final, 121);
  const r=compound(100, [-100, 1000]); near(r.final, 0); near(r.geometric, -100);
  assert.equal(recovery(100), null); assert.equal(recovery(0), 0);
});
test('cost examples match independently precomputed results and zero costs coincide', () => {
  const r=costs(1000000, .3, .2, 100);
  near(r.before, 1349252.7193664927, 1e-6); near(r.after, 1105115.6977207558, 1e-6);
  near(costs(1000000,.3,0,100).difference,0);
  near(costs(1000000,.3,.3,100).after,1000000);
  assert.ok(costs(1000000,.3,.4,100).after<1000000);
});
test('position floors shares, reserves costs, and observes cash and risk separately', () => {
  assert.deepEqual(position(10000000,1,50000,47500,.2,20), {
    shares:38, budget:100000, plannedLoss:98800, amount:1900000, reservedCost:3800, limitedBy:'손실 예산'
  });
  const limited=position(10000000,1,50000,47500,.2,10);
  assert.equal(limited.shares,19); assert.equal(limited.limitedBy,'투자 상한');
  assert.ok(limited.amount+limited.reservedCost<=1000000);
  assert.equal(position(100,1,50000,47500,.2,20).shares,0);
});
test('empty, nonfinite, impossible and overflowing assumptions are rejected', () => {
  for(const invalid of ['',null,NaN,Infinity,'=1+1']) {
    assert.throws(()=>compound(invalid,[1])); assert.throws(()=>recovery(invalid));
  }
  assert.throws(()=>compound(100,[])); assert.throws(()=>compound(100,[-101]));
  assert.throws(()=>compound(100,[...Array(101)].map(()=>1)));
  assert.throws(()=>compound(1e12,[1000,1000,1000,1000]));
  assert.throws(()=>costs(100,-99,2,1)); assert.throws(()=>costs(100,1,.2,1.5));
  assert.throws(()=>costs(1e12,100,.2,1000));
  assert.throws(()=>position(10000,1,100,100,0,20));
  assert.throws(()=>position(10000,1,100,90,0,101));
  assert.throws(()=>position(10000,1,1e308,90,99,20));
  assert.throws(()=>position(10000,1,1e-20,0,0,20));
  assert.throws(()=>recovery(-1)); assert.throws(()=>recovery(101));
});
