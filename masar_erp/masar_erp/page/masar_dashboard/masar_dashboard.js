frappe.pages['masar-dashboard'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __('لوحة التحكم المالية'),
    single_column: true
  });
  page.set_primary_action(__('تحديث البيانات'), () => load_dashboard(), 'refresh');
  const root = $(`
    <div class="masar-dashboard" dir="rtl">
      <div class="masar-dashboard-head">
        <div><div class="masar-eyebrow">MASAR ERP · FINANCE</div><h2>نظرة عامة على أعمالك</h2><p class="text-muted">مؤشرات مباشرة من سجلات الشركة المصرح لك بها</p></div>
        <div class="masar-company"><label>الشركة</label><div class="company-picker"></div></div>
      </div>
      <div class="masar-kpis">
        <section class="masar-kpi"><span>إجمالي المدين</span><strong data-kpi="debit">—</strong><small>من دفتر الأستاذ العام</small></section>
        <section class="masar-kpi"><span>إجمالي الدائن</span><strong data-kpi="credit">—</strong><small>من دفتر الأستاذ العام</small></section>
        <section class="masar-kpi"><span>صافي الحركة</span><strong data-kpi="net">—</strong><small>الدائن ناقص المدين</small></section>
        <section class="masar-kpi"><span>أصناف بالمخزون</span><strong data-kpi="items">—</strong><small data-kpi="quantity">الكمية: —</small></section>
        <section class="masar-kpi"><span>مبيعات هذا الشهر</span><strong data-kpi="sales">—</strong><small>فواتير مبيعات مرحلة</small></section>
        <section class="masar-kpi"><span>مشتريات هذا الشهر</span><strong data-kpi="purchases">—</strong><small>فواتير مشتريات مرحلة</small></section>
        <section class="masar-kpi"><span>ذمم العملاء المستحقة</span><strong data-kpi="receivables">—</strong><small>مستحقات فواتير الشهر</small></section>
        <section class="masar-kpi"><span>ذمم الموردين المستحقة</span><strong data-kpi="payables">—</strong><small>مستحقات فواتير الشهر</small></section>
      </div>
      <div class="masar-dashboard-grid">
        <section class="masar-panel masar-chart-panel"><div class="masar-panel-title"><div><h3>الحركة المالية</h3><p>آخر ستة أشهر · مدين ودائن</p></div><span class="masar-live-dot">بيانات فعلية</span></div><div class="masar-chart" aria-label="رسم بياني للحركة المالية"></div><div class="masar-legend"><span class="debit-key">المدين</span><span class="credit-key">الدائن</span></div></section>
        <section class="masar-panel"><div class="masar-panel-title"><div><h3>أحدث فواتير المبيعات</h3><p>آخر المستندات المرحلة</p></div><button class="btn btn-xs btn-default" data-route="Sales Invoice">عرض الكل</button></div><div class="masar-invoices"></div></section>
        <section class="masar-panel"><div class="masar-panel-title"><div><h3>أحدث فواتير المشتريات</h3><p>آخر فواتير الموردين المرحلة</p></div><button class="btn btn-xs btn-default" data-route="Purchase Invoice">عرض الكل</button></div><div class="masar-purchases"></div></section>
        <section class="masar-panel"><div class="masar-panel-title"><div><h3>آخر القيود اليومية</h3><p>قيود اليومية المعتمدة</p></div><button class="btn btn-xs btn-default" data-route="Journal Entry">عرض الكل</button></div><div class="masar-journals"></div></section>
      </div>
      <div class="masar-footnote">تعرض اللوحة ما تسمح به صلاحيات حسابك فقط. الأرقام لا تشمل أي بيانات تجريبية.</div>
    </div>`);
  $(page.body).append(root);
  root.on("click", "[data-route]", function () { frappe.set_route("List", $(this).attr("data-route")); });
  root.on("click", "[data-open-name]", function () { frappe.set_route("Form", $(this).attr("data-open-doctype"), $(this).attr("data-open-name")); });
  const company = frappe.ui.form.make_control({
    parent: root.find('.company-picker'),
    df: {fieldtype:'Link', options:'Company', fieldname:'company', placeholder:__('اختر الشركة'), reqd:1},
    render_input:true
  });
  company.$input.on('change', load_dashboard);
  root.data('company-control', company);
  frappe.call({method:'frappe.client.get_list', args:{doctype:'Company', fields:['name'], order_by:'name asc', limit_page_length:100}})
    .then(r => {
      const rows = r.message || [];
      const preferred = frappe.defaults.get_user_default('Company');
      if (preferred && rows.some(x => x.name === preferred)) company.set_value(preferred);
      else if (rows.length === 1) company.set_value(rows[0].name);
      else if (rows.length) company.set_value(rows[0].name);
      load_dashboard();
    });
  function money(value, currency) {
    return new Intl.NumberFormat(frappe.boot.lang || 'ar-EG', {style:'currency', currency:currency || 'EGP', maximumFractionDigits:0}).format(value || 0);
  }
  function escape(value) { return $('<div>').text(value == null ? '' : value).html(); }
  function render_chart(points) {
    const max = Math.max(1, ...points.flatMap(p => [p.debit, p.credit]));
    const width = 720, height = 230, left = 12, bottom = 195;
    const x = i => left + i * ((width-left-12) / Math.max(1, points.length-1));
    const y = v => bottom - (v/max)*165;
    const line = key => points.map((p,i) => (i?'L':'M') + x(i) + ',' + y(p[key])).join(' ');
    const area = key => line(key) + ` L${x(points.length-1)},${bottom} L${x(0)},${bottom} Z`;
    const labels = points.map((p,i)=>`<text x="${x(i)}" y="220" text-anchor="middle">${escape(p.month.slice(5))}</text>`).join('');
    return `<svg viewBox="0 0 ${width} ${height}" role="img"><defs><linearGradient id="masarDebit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c6fbd" stop-opacity=".25"/><stop offset="1" stop-color="#2c6fbd" stop-opacity="0"/></linearGradient><linearGradient id="masarCredit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#31a77b" stop-opacity=".2"/><stop offset="1" stop-color="#31a77b" stop-opacity="0"/></linearGradient></defs><path d="${area('debit')}" fill="url(#masarDebit)"/><path d="${area('credit')}" fill="url(#masarCredit)"/><path d="${line('debit')}" fill="none" stroke="#2c6fbd" stroke-width="3" stroke-linecap="round"/><path d="${line('credit')}" fill="none" stroke="#31a77b" stroke-width="3" stroke-linecap="round"/>${labels}</svg>`;
  }
  let activeRequest = 0;
  function load_dashboard() {
    const selected = company.get_value();
    if (!selected) return;
    const requestId = ++activeRequest;
    root.find('.masar-panel').addClass('masar-loading');
    frappe.call({method:'masar_erp.masar_erp.page.masar_dashboard.masar_dashboard.get_dashboard_data', args:{company:selected}})
      .then(r => {
        if (requestId !== activeRequest) return;
        const d = r.message || {}, currency = d.currency || 'EGP';
        root.find('[data-kpi="debit"]').text(money(d.financial.debit,currency));
        root.find('[data-kpi="credit"]').text(money(d.financial.credit,currency));
        root.find('[data-kpi="net"]').text(money(d.financial.net,currency));
        root.find('[data-kpi="items"]').text((d.inventory.items || 0).toLocaleString());
        root.find('[data-kpi="sales"]').text(money(d.sales.month_total,currency));
        root.find('[data-kpi="purchases"]').text(money(d.purchases.month_total,currency));
        root.find('[data-kpi="receivables"]').text(money(d.sales.outstanding,currency));
        root.find('[data-kpi="payables"]').text(money(d.purchases.outstanding,currency));
        root.find('[data-kpi="quantity"]').text('إجمالي الكمية: ' + (d.inventory.quantity || 0).toLocaleString());
        root.find('.masar-chart').html(d.trend && d.trend.length ? render_chart(d.trend) : '<div class="masar-empty">لا توجد حركات مالية ضمن الفترة المحددة</div>');
        const invoices = d.recent_invoices || [];
        root.find('.masar-invoices').html(invoices.length ? invoices.map(inv => `<div class="masar-invoice" data-open-doctype="Sales Invoice" data-open-name="${escape(inv.name)}"><div><b>${escape(inv.customer)}</b><small>${escape(inv.name)} · ${escape(inv.posting_date)}</small></div><strong>${money(inv.base_grand_total,currency)}</strong></div>`).join('') : '<div class="masar-empty">لا توجد فواتير مبيعات متاحة</div>');
        const purchases = d.recent_purchase_invoices || [];
        root.find('.masar-purchases').html(purchases.length ? purchases.map(inv => `<div class="masar-invoice" data-open-doctype="Purchase Invoice" data-open-name="${escape(inv.name)}"><div><b>${escape(inv.supplier)}</b><small>${escape(inv.name)} · ${escape(inv.posting_date)}</small></div><strong>${money(inv.base_grand_total,currency)}</strong></div>`).join('') : '<div class="masar-empty">لا توجد فواتير مشتريات متاحة</div>');
        const journals = d.recent_journal_entries || [];
        root.find('.masar-journals').html(journals.length ? journals.map(entry => `<div class="masar-invoice" data-open-doctype="Journal Entry" data-open-name="${escape(entry.name)}"><div><b>${escape(entry.name)}</b><small>${escape(entry.posting_date)} · ${escape(entry.user_remark || 'قيد يومية')}</small></div><strong>${money(entry.total_debit,currency)}</strong></div>`).join('') : '<div class="masar-empty">لا توجد قيود يومية متاحة</div>');
      })
      .catch(() => { if (requestId === activeRequest) frappe.msgprint(__('تعذر تحميل بيانات اللوحة. تحقق من صلاحياتك واتصال الخادم.')); })
      .finally(() => { if (requestId === activeRequest) root.find('.masar-panel').removeClass('masar-loading'); });
  }
};
