$(document).ready(function () {


    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');


    // Date time Widget Area
    $(function () {
        $("#connectionAt").datepicker({
            changeMonth: true,
            changeYear: true,
            dateFormat: 'yy-mm-dd'
        });
        $("#connectionAt").datepicker('setDate', 'today')

        $("#date").datepicker({
            changeMonth: true,
            changeYear: true,
            dateFormat: 'yy-mm-dd'
        });
        $("#date").datepicker('setDate', 'today');

    });


    // DataTable Initialization
    $('#customer_table_id').DataTable({
        scrollX: true
    })
    $('#singel-report-table').DataTable()


    // get Last Customer id and Next Customer id set in customer page
    $('#area').change(function () {
        let areaId = $(this).val()
        $.get('/customers/next_id/' + areaId + '/', function (data) {
            $('#id').val(data.nextId)
        })
    })





    //preview client info when insert client data.
    $('#add-customers').submit(function (event) {
        console.log($(this).serialize())
        $.ajax({
            url: '/api/customers/',
            method: 'post',
            data: $(this).serialize(),
            dataType: 'json',
            beforeSend: function (request) {
                request.setRequestHeader('X-CSRFToken', csrftoken)
            },
            success: function (data) {
                if (!data.error) {
                    console.log(data)
                    console.log('success')
                    location.reload()
                } else {
                    console.log(data.error.id)
                    $("#alertDiv").html(`
                        <div id="alert" class="alert alert-danger alert-dismissible show fade mt-3" role="alert">
                            <strong>গ্রাহক যুক্ত হয়নি</strong>
                            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                    `)
                    console.log('error')
                }

            },
            error: function (erro) {
                console.log(error)
            }
        })
        event.preventDefault()
    })

    // Customer Update Funtionality
    $(document).on('click', '.update-btn', function () {
        let id = $(this).data('id')


        $.get('/api/customers/' + id + '/', function (data) {
            $("#customerModal").modal('show') //customer modal show
            $('#customer-add-submit').html('পরিবর্তন করুন') // submit btn chang
            $("#id").prop('disabled', true)
            $("#area").prop('disabled', true)


            $('#id').val(data.id)
            $('#name').val(data.name)
            $('#fatherName').val(data.fatherName)
            $('#address').val(data.address)
            $('#area').val(data.area.id)
            $('#mobileNumber').val(data.mobileNumber)
            $('#nidNumber').val(data.nidNumber)
            $('#connectionAt').val(data.connectionAt)
            $('#connectionFee').val(data.connectionFee)
            $('#tv').val(data.tv)
            $('#occupation').val(data.occupation)
            $('#monthlyCharge').val(data.monthlyCharge)
            $('#permanentDiscount').val(data.permanentDiscount)
        })


        // customer button action
        $('#customer-add-submit').click(function (event) {
            event.preventDefault()
            let name = $('#name').val()
            let fatherName = $('#fatherName').val()
            let address = $('#address').val()
            let area = $('#area').val()
            let mobileNumber = $("#mobileNumer").val()
            let nidNumber = $("#nidNumber").val()
            let tv = $('#tv').val()
            let occupation = $('#occupation').val()
            let monthlyCharge = $('#monthlyCharge').val()
            let permanentDiscount = $('#permanentDiscount').val()

            let contextData = {
                name,
                fatherName,
                address,
                area,
                mobileNumber,
                nidNumber,
                tv,
                occupation,
                monthlyCharge,
                permanentDiscount
            }

            $.ajax({
                url: '/api/customers/' + id + '/',
                method: 'put',
                data: contextData,
                dataType: 'json',
                beforeSend: function (request) {
                    request.setRequestHeader('X-CSRFToken', csrftoken)
                },
                success: function (responseData) {
                    console.log(responseData)
                    if (!responseData.error) {
                        console.log(responseData)
                        console.log('success')
                        location.reload()
                    } else {
                        console.log(responseData.error.id)
                        $("#alertDiv").html(`
                            <div id="alert" class="alert alert-danger alert-dismissible show fade mt-3" role="alert">
                                <strong>গ্রাহক যুক্ত হয়নি</strong>
                                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                        `)
                    }

                },
                error: function (erro) {
                    console.log(error)
                }
            })


        })
    })





    //for bill query by ID NUMBER
    $("#billbtn").click(function (e) {
        e.preventDefault()

        paidBills = []
        totalAmount = 0
        var customerId = $("#billid").val();
        if (customerId) {
            getCustomerDetails(customerId);
        } else {
            $("#userdetails").html("<h4 class='text-danger'> আইডি প্রদান করুন </h4>");
            $("#payment").hide();
        }

    });

    // active inactive code here
    $(document).on('click', '.inactive-btn', function () {
        let id = $(this).data('id')
        let isActive = $(this).data('isactive') == 'inactive' ? false : true

        if (confirm("Are you Sure?")) {
            $.ajax({
                beforeSend: function (request) {
                    request.setRequestHeader('X-CSRFToken', csrftoken)
                },
                method: 'POST',
                url: "/customers/" + id + '/inactive/',
                dataType: 'json',
                cache: true,
                data: {
                    isActive: JSON.stringify(isActive)
                },
                success: function (data) {
                    console.log(data)
                    location.reload()
                }
            })
        }

    })


    // Delete funtionality here 
    $(document).on('click', '.delete-btn', function () {
        let id = $(this).data('id')

        if (confirm('Are You sure For Delete')) {
            $.ajax({
                method: 'delete',
                url: '/api/customers/' + id + '/',
                beforeSend: function (request) {
                    request.setRequestHeader('X-CSRFToken', csrftoken)
                },
                success: function (data) {
                    console.log(data)
                    location.reload()
                }
            })
        }
    })



    //get Customer information
    function getCustomerDetails(customerId) {
        $("#name").val('');
        // $("#userdetails").hide();
        $("#payment-info").html("");
        $("#amount").prop("disabled", true);
        $("#discount").prop("disabled", true);
        $("#amount").val("");
        $("#discount").val("");

        $("#billbtn").prop("disabled", true);
        $("#billbtn").html('<span class="spinner-border spinner-border-sm"></span>')


        $.ajax({
            type: "GET",
            url: '/api/customers/' + customerId + "/",
            dataType: "json",
            cache: false,
            error: function (xhr, ajaxOptions, thrownError) {
                $("#billbtn").prop("disabled", false);
                $("#billbtn").html('<i class="fa fa-search" ></i>')

                $("#billbtn").prop("disabled", false);
                $("#billbtn").html('<i class="fa fa-search"></i>')
                $("#userdetails").html("<h4 class='text-danger'> এই আইডিতে তথ্য পাওয়া যায়নি।</h4>");
                $("#payment").hide();
            },
            success: function (customer) {

                // Calling bill info
                getBills(customerId)

                let mobile = (customer.monbileNumber) ? "যুক্ত করা হয়নি" : customer.mobileNumber;
                let condition = customer.isActive ? '<td class="text-light bg-success rounded">সংযোগকৃত</td>' : '<td class="text-light bg-danger rounded">বিচ্ছিন্ন</td>'
                let duesInfo = customer.totalDues !== 0 ? "<span id='totalDues'>" + customer.totalDues + "</span>  টাকা<small class='text-light bg-danger rounded ml-2 px-2'> <span id='totalMonth'></span> মাস</small>" : 'নেই'

                // customer details div
                $("#userdetails").html(
                    '<h5 class="text-success">আইডি : <span class="text-danger">' + customer.id + '</span></h5><hr>' +

                    '<table>' +
                    '<tr>' +
                    '<td><h3 class="text-info">নাম</h3></td>' +
                    '<td class="px-3">:</td><td><h3 class="text-danger">' + customer.name + '</h3></td>' +
                    '</tr>' +
                    '<tr>' +
                    '<td class="text-info">পিতা</td>' +
                    '<td class="px-3">:</td><td class="text-success">' + customer.fatherName + '</td>' +
                    '</tr>' +
                    '<tr>' +
                    '<td class="text-info">ঠিকানা</td>' +
                    '<td class="px-3">:</td><td class="text-success">' + customer.address + '</td>' +
                    '</tr>' +
                    '<tr>' +
                    '<td class="text-info">এলাকা</td>' +
                    '<td class="px-3">:</td><td class="text-success">' + customer.area.name + '</td>' +
                    '</tr>' +
                    '<tr>' +
                    '<td class="text-info">পেশা</td>' +
                    '<td class="px-3">:</td><td class="text-success">' + customer.occupation + '</td>' +
                    '</tr>' +
                    '<tr>' +
                    '<td class="text-info">অবস্থা</td>' +
                    '<td class="px-3">:</td>' + condition +
                    '</tr>' +
                    '<tr>' +
                    '<td class="text-info">মোবাইল নং</td>' +
                    '<td class="px-3">:</td><td class="text-success">' + mobile + '</td>' +
                    '</tr>' +
                    '<tr>' +
                    '<td class="text-danger"><h4>বকেয়া</h4></td>' +
                    '<td class="px-3">:</td><td class="text-success">' +
                    '<h4 id="duesDiv" class="text-danger">' + duesInfo + '</h4>' +
                    '</td>' +
                    '</tr>' +
                    '</table>'
                );


            }
        });
    }


    //get all Bills by customer id
    function getBills(customerId) {

        $.ajax({
            method: "GET",
            url: '/api/customers/' + customerId + '/bills/',
            cache: false,
            success: function (bills) {
                $("#billbtn").prop("disabled", false);
                $("#billbtn").html('<i class="fa fa-search"></i>')

                $("#billCheckbox").empty()

                var totalMonth = bills.length
                if (totalMonth > 0) {
                    $("#payment").show();
                    $("#totalMonth").html(totalMonth)

                    for (let i = 0; i < totalMonth; i++) {
                        $("#billCheckbox").append(
                            '<div class="custom-control custom-checkbox">' +
                            '<input class="month custom-control-input" tabindex="1" type="checkbox"  value="' + bills[i].monthlyCharge + '" id="' + bills[i].id + '">' +
                            '<label class="custom-control-label" for="' + bills[i].id + '">' +
                            '<h5> ' + bills[i].month + '-' + bills[i].year + ' <small class="text-light bg-danger px-2 rounded">' + bills[i].monthlyCharge + '</small></h5>' +
                            '</label>' +
                            '</div>'
                        );
                    }
                    // $('#totalDues').html(totalDues)

                } else {
                    $("#payment").hide();
                }
            }
        })
    }



    //for checkbox select
    let paidBills = [];
    let totalAmount = 0;

    $(document).on('change', '.month', function () {
        if ($(this).prop("checked")) {
            paidBills.push($(this).attr("id"));
            totalAmount += parseInt($(this).val())
        } else {
            for (var i in paidBills) {
                if (paidBills[i] == $(this).attr("id")) {
                    totalAmount -= parseInt($(this).val())
                    paidBills.splice(i, 1);
                    break;
                }
            }
        }
        $("#amount").val(totalAmount);
    })



    // Make Payments
    $("#paybtn").click(function (event) {
        event.preventDefault()




        if (paidBills.length > 0) {
            $("#paybtn").prop('disabled', true)
            $("#paybtn").html('<span class="spinner-border spinner-border-sm"></span>')


            let userid = $("#billid").val();
            let paidAmount = parseInt($("#amount").val()) || 0;
            let discount = parseInt($("#discount").val()) || 0;
            let txnId = parseInt($("#receipt").val()) || 0;
            let bills = paidBills;
            let isSms = $("#sms").prop('checked') ? true : false


            let context = {
                bills: bills,
                paidAmount: paidAmount,
                discount: discount,
                txnId: txnId,
                isSms: isSms
            }

            $.ajax({
                url: "/api/customers/" + userid + "/payments/",
                type: "POST",
                data: JSON.stringify(context),
                contentType: 'application/json',
                dataType: "json",
                cache: false,
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                },
                error: function (error) {
                    console.log(error)
                },

                success: function (data) {
                    let customerId = $("#billid").val();
                    $("#paybtn").prop('disabled', false)
                    $("#paybtn").html('পরিশোধ')

                    if (data.success) {
                        getCustomerDetails(customerId)
                        $("#payment-info").html("<span class='text-success'>পরিশোধ হয়েছে</span>")
                    } else {
                        getCustomerDetails(customerId)
                        $("#payment-info").html("অন্য কেউ পরিশোধ করেছে")
                    }
                    console.log(data)
                },
                complete: function () {
                    paidBills = []
                    totalAmount = 0
                }

            });
        } else {
            alert("মাস নির্বাচন করা হয়নি।");
        }
    })



    //for bill query by Name OR Mobile
    $(document).on("click", ".userid", function () {
        let userid = $(this).find(".idvalue").html();
        getCustomerDetails(userid);
        $("#billid").val(userid);
    })

    //for found unknown client by name and mobile number
    $("#namebtn").click(function (e) {
        e.preventDefault();
        $("#userdetails").html('');
        $("#payment").hide();

        let name = $("#name").val();
        if (name != '') {
            $.ajax({
                url: "/customers/name_or_mobile/",
                type: "GET",
                dataType: "json",
                cache: false,
                data: {
                    "value": name
                },
                success: function (data) {
                    if (data.length != 0) {
                        for (var i = 0; i < data.length; i++) {

                            $("#userdetails").append(
                                '<div  class="userid bordered rounded shadow p-3 mt-3 bg-warning">' +
                                '<table>' +
                                '<tr>' +
                                '<td class="text-danger"><h5>আইডি  </h5></td>' +
                                '<td class="px-3">:</td><td><h3 class="idvalue text-danger">' + data[i].id + '</h3></td>' +
                                '</tr>' +
                                '<tr>' +
                                '<td >নাম  </td><td class="px-3">:</td>' +
                                '<td class="text-info">' + data[i].name + '</td>' +
                                '</tr><tr><td>পিতা  </td><td class="px-3">:</td>' +
                                '<td class="text-info">' + data[i].fatherName + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                '<td>ঠিকানা  </td><td class="px-3">:</td>' +
                                '<td class="text-info">' + data[i].address + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                '<td>এলাকা  </td>' +
                                '<td class="px-3">:</td>' +
                                '<td class="text-info">' + data[i].area.name + '</td>' +
                                '</tr>' +
                                '</table>' +
                                '</div>'
                            );

                        }
                    } else {
                        $("#userdetails").html("<h4 class='text-danger'>তথ্য পাওয়া যায়নি।</h4>");
                    }
                }
            });
        } else {
            $("#userdetails").html("<h4 class='text-info '>সঠিক তথ্য প্রদান করুন।</h4>");
        }

    });

    // for mouse hove effect searc result
    $(document).on("mouseover", ".userid", function () {
        $(this).css('cursor', 'pointer');
    })

    // for amount field enable
    $("#amountDiv").on("dblclick", function () {
        $("#amount").prop("disabled", false);
        $("#amount").focus();
    })
    // for discount field enable
    $("#discountDiv").on("dblclick", function () {
        $("#discount").prop("disabled", false);
        $("#discount").focus();
    })

    $("#amount").click(function () {
        this.select();
    })




    // Check sms balance and expiry date
    $('#smscheck').click(function () {
        $('#sms-info').html(`<div class='bg-primary text-light mb-3 p-3 rounded'>
            <span>অপেক্ষা করুন................</span>
        </div>`)

        $.get('/sms_check/', function (data) {
            if (data.balance != 0) {
                $('#sms-info').html(`<div class='bg-primary text-light mb-3 p-3 rounded'>
                এসএমএস রয়েছে 
                <span class='bg-danger px-2 rounded'>${data.balance}</span>
                টি। মেয়াদ আছে 
                <span class='bg-danger px-2 rounded' >${data.expiry}</span> 
                পর্যন্ত।";
            </div>`)
            } else {
                $('#sms-info').html(`<div class='bg-primary text-light mb-3 p-3 rounded'>
                        <span class='bg-danger px-2 rounded'>এসএমএস নেই।</span>
                        <a class='text-light' href='http://sms.greenweb.com.bd'>কিনতে এখানে ক্লিক করুন</a>
                    </div>`)
            }

        })
    })
})