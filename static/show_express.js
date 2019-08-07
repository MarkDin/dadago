function show_express(data) {
    KDNWidget.run({
        serviceType: 'B',
        expCode: data.exp_code,
        expNo: data.exp_number,
        showType: 'normal',
        container: 'logistics_box'
    });
}