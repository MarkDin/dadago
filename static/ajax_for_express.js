function query_express() {//1233542345
    // 获取输入的快递单号
    var phone_number = document.getElementById('phone_number').value;
    if (phone_number == null || phone_number === '') {
        alert("输入为空,请重新输入");
    } else {
        // 发送给后端的数据
        var data = {'phone_number': phone_number};
        // 通过ajax方式发送data给后端函数,获取返回的快递公司代号
        $.ajax({
            type: 'POST',
            url: '/express_query',
            data: data,
            dataType: 'json',
            success: function (D) {

                // 调用快递鸟js接口显示查询结果

                // 当数据库存在快递单号
                if (D.flag === '0') {
                    // 如果单号无法查询出对应快递公司
                    if (D.expCode === 'error') {
                        alert('无法检测出单号对应的快递公司');
                    } else {
                        KDNWidget.run({
                            serviceType: D.serviceType,
                            expCode: D.expCode,
                            expNo: D.expNo,
                            showType: 'normal',
                            container: D.container
                        });
                    }

                } else {
                    alert('该手机号码不存在对应单号,请核对后输入');
                }

            }

        })
    }

}