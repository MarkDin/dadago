function check() {
    // 获取输入的快递单号
    var phone_number = document.getElementById('phone_number').value;
    if (phone_number == null || phone_number === '') {
        alert("输入为空,请重新输入");
    } else {
        // form.action='/express_query';
        // form.submit();
        // document.form.submit();
        document.getElementById("myForm").submit()
    }

}