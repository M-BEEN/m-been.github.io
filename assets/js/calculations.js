// Pure educational calculations. Rates are percentages at the API boundary.
function finite(value, label) {
  if (value === '' || value === null || !Number.isFinite(Number(value))) throw new Error(`${label}에 유효한 숫자를 입력해 주세요.`);
  return Number(value);
}

export function compound(initial, rates) {
  initial = finite(initial, '시작 금액');
  if (initial <= 0 || initial > 1e12) throw new Error('시작 금액은 0원 초과, 1조 원 이하로 입력해 주세요.');
  if (!rates.length || rates.length > 100) throw new Error('수익률을 1개부터 100개까지 입력해 주세요.');
  rates = rates.map(r => finite(r, '수익률'));
  if (rates.some(r => r < -100 || r > 1000)) throw new Error('각 수익률은 −100%부터 1,000%까지 입력해 주세요.');
  let balance = initial;
  const steps = rates.map((rate, i) => {
    const before = balance;
    balance *= 1 + rate / 100;
    return { period: i + 1, rate, before, balance };
  });
  if (!Number.isFinite(balance) || balance > 1e15) throw new Error('계산 결과가 너무 큽니다. 수익률이나 기간 수를 줄여 주세요.');
  return { steps, final: balance, total: (balance / initial - 1) * 100,
    arithmetic: rates.reduce((a, b) => a + b, 0) / rates.length,
    geometric: ((balance / initial) ** (1 / rates.length) - 1) * 100 };
}

export function recovery(loss) {
  loss = finite(loss, '손실률');
  if (loss < 0 || loss > 100) throw new Error('손실률은 0%부터 100%까지 입력해 주세요.');
  return loss === 100 ? null : loss / (100 - loss) * 100;
}

export function costs(initial, gross, fee, rounds) {
  initial = finite(initial, '시작 금액'); gross = finite(gross, '회당 수익률');
  fee = finite(fee, '회당 비용률'); rounds = finite(rounds, '거래 횟수');
  if (initial <= 0 || initial > 1e12) throw new Error('시작 금액은 0원 초과, 1조 원 이하로 입력해 주세요.');
  if (!Number.isInteger(rounds) || rounds < 1 || rounds > 1000) throw new Error('거래 횟수는 1부터 1,000까지의 정수로 입력해 주세요.');
  if (fee < 0 || fee >= 100 || gross <= -100 || gross > 100 || gross - fee <= -100) throw new Error('비용률은 0% 이상 100% 미만, 회당 수익률은 −100% 초과 100% 이하이며 비용 차감 뒤에도 −100%를 넘어야 합니다.');
  // Fee is an assumed round-trip cost divided by each trade's starting capital.
  const before = initial * (1 + gross / 100) ** rounds;
  const after = initial * (1 + (gross - fee) / 100) ** rounds;
  if (!Number.isFinite(before) || before > 1e15 || !Number.isFinite(after)) throw new Error('계산 결과가 너무 큽니다. 수익률이나 거래 횟수를 줄여 주세요.');
  return { before, after, difference: before - after,
    beforePct: (before / initial - 1) * 100, afterPct: (after / initial - 1) * 100 };
}

export function position(capital, risk, entry, stop, fee, cap) {
  [capital, risk, entry, stop, fee, cap] = [capital, risk, entry, stop, fee, cap].map(v => finite(v, '입력값'));
  if (capital <= 0 || capital > 1e12 || entry < .01 || entry > 1e12 || stop < 0 || stop >= entry) throw new Error('총자금은 0원 초과 1조 원 이하, 매수가는 0.01원 이상 1조 원 이하, 청산 가정가는 0 이상 매수가 미만이어야 합니다.');
  if (risk <= 0 || risk > 100 || cap <= 0 || cap > 100 || fee < 0 || fee >= 100) throw new Error('손실 예산과 투자 상한은 0% 초과 100% 이하, 비용률은 0% 이상 100% 미만으로 입력해 주세요.');
  const budget = capital * risk / 100;
  const unitLoss = entry - stop + entry * fee / 100;
  const unitCost = entry * (1 + fee / 100); // Reserve all estimated round-trip costs up front.
  const byRisk = Math.floor(budget / unitLoss);
  const byCash = Math.floor((capital * cap / 100) / unitCost);
  const shares = Math.min(byRisk, byCash);
  return { shares, budget, plannedLoss: shares * unitLoss, amount: shares * entry,
    reservedCost: shares * entry * fee / 100, limitedBy: byRisk <= byCash ? '손실 예산' : '투자 상한' };
}
