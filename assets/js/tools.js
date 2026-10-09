import { compound, recovery, costs, position } from './calculations.js';
const money = n => new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 2 }).format(n) + '원';
const pct = n => (n > 0 ? '+' : '') + n.toLocaleString('ko-KR', { minimumFractionDigits: 2, maximumFractionDigits: 4 }) + '%';
function element(tag, text, className) {
  const el = document.createElement(tag); el.textContent = text;
  if (className) el.className = className;
  return el;
}
document.querySelectorAll('[data-calculator]').forEach(root => {
  const form = root.querySelector('form'), result = root.querySelector('[data-result]');
  const error = root.querySelector('[data-error]'), download = root.querySelector('[data-download]');
  let rows = null;
  form.querySelector('fieldset').disabled = false;
  function clear() { rows = null; result.hidden = true; error.hidden = true; download.hidden = true; }
  function calculate() {
    clear(); result.replaceChildren();
    const input = Object.fromEntries(new FormData(form));
    try {
      let title, main, detail;
      if (root.dataset.calculator === 'compound') {
        const rates = input.rates.trim().replaceAll('−', '-').split(/[,\s]+/);
        const r = compound(input.initial, rates), recover = recovery(input.loss);
        title = '누적 수익률'; main = pct(r.total);
        detail = `끝 금액 ${money(r.final)} · 기간당 산술평균 ${pct(r.arithmetic)} · 기간당 기하평균 ${pct(r.geometric)}. `;
        detail += recover === null ? '100% 손실로 잔액이 0이면 유한한 상승률로 회복할 수 없습니다.' : `${input.loss}% 손실을 회복하려면 ${pct(recover)} 상승이 필요합니다.`;
        result.append(element('h3', title), element('p', main, 'result-main'), element('p', detail, 'result-detail'));
        const chart = element('div', '', 'calc-chart'); chart.setAttribute('aria-hidden', 'true');
        const balances = [Number(input.initial), ...r.steps.map(s => s.balance)], max = Math.max(...balances);
        balances.forEach(value => { const bar = element('span', ''); bar.style.height = Math.max(.2, value / max * 100) + '%'; chart.append(bar); });
        result.append(chart);
        const wrap = element('div', '', 'calc-table'), table = document.createElement('table');
        const caption = element('caption', '기간별 계산 내역'); table.append(caption);
        const head = document.createElement('thead'), tr = document.createElement('tr');
        ['기간', '수익률', '시작 금액', '끝 금액'].forEach(t => { const th = element('th', t); th.scope = 'col'; tr.append(th); });
        head.append(tr); table.append(head); const body = document.createElement('tbody');
        r.steps.forEach(s => { const row = document.createElement('tr'); [s.period, pct(s.rate), money(s.before), money(s.balance)].forEach(v => row.append(element('td', v))); body.append(row); });
        table.append(body); wrap.append(table); result.append(wrap);
        rows = [['kind', 'fictional_compounding'], ['initial', input.initial], ['period', 'rate_pct', 'before', 'after'], ...r.steps.map(s => [s.period, s.rate, s.before, s.balance]), ['assumed_loss_pct', input.loss], ['required_recovery_pct', recover === null ? 'undefined_zero_balance' : recover]];
      } else if (root.dataset.calculator === 'costs') {
        const r = costs(input.initial, input.gross, input.fee, input.rounds);
        title = '비용을 반영한 끝 금액'; main = money(r.after);
        detail = `비용 전 ${money(r.before)} (${pct(r.beforePct)}) → 비용 반영 후 ${money(r.after)} (${pct(r.afterPct)}). 두 끝 금액의 차이 ${money(r.difference)}는 비용과 재투자 효과를 합친 값이며, 수수료 청구액의 합계가 아닙니다.`;
        rows = [['kind', 'fictional_fixed_return_cost_model'], ...Object.entries(input), ...Object.entries(r)];
      } else {
        const r = position(input.capital, input.risk, input.entry, input.stop, input.fee, input.cap);
        title = '가정한 예산 안에서 계산한 정수 수량'; main = `${r.shares.toLocaleString('ko-KR')}주`;
        detail = `매수금액 ${money(r.amount)} · 비용 예비금 ${money(r.reservedCost)} · 청산 가정가 체결 시 손실 ${money(r.plannedLoss)} / 예산 ${money(r.budget)}. 수량을 제한한 조건: ${r.limitedBy}. 실제 손실의 상한이나 매수 추천이 아닙니다.`;
        rows = [['kind', 'fictional_long_only_position'], ...Object.entries(input), ...Object.entries(r)];
      }
      if (root.dataset.calculator !== 'compound') result.append(element('h3', title), element('p', main, 'result-main'), element('p', detail, 'result-detail'));
      result.hidden = false; download.hidden = false;
    } catch (e) { error.textContent = e.message; error.hidden = false; }
  }
  form.addEventListener('submit', e => { e.preventDefault(); calculate(); });
  form.addEventListener('input', clear);
  // The reset event runs before the browser restores default input values.
  form.addEventListener('reset', () => setTimeout(calculate, 0));
  download.addEventListener('click', () => {
    if (!rows) return;
    // All cells are numbers or controlled identifiers; user-entered formula strings never reach CSV.
    const csv = '\ufeff' + rows.map(row => row.map(v => '"' + String(v).replaceAll('"', '""') + '"').join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a'); a.href = url; a.download = `yieldrecipe-${root.dataset.calculator}-example.csv`; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  calculate();
});
