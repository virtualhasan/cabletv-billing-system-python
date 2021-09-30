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
        $("#connectionAt, #user-date").datepicker({
            changeMonth: true,
            changeYear: true,
            dateFormat: 'yy-mm-dd'
        });
        $("#connectionAt, #user-date").datepicker('setDate', 'today')

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
            // $('#permanentDiscount').val(data.permanentDiscount)
        })


        // customer button action
        $('#customer-add-submit').click(function (event) {
            event.preventDefault()
            let name = $('#name').val()
            let fatherName = $('#fatherName').val()
            let address = $('#address').val()
            let area = $('#area').val()
            let mobileNumber = $("#mobileNumber").val()
            let nidNumber = $("#nidNumber").val()
            let connectionFee = $('#connectionFee').val()
            let tv = $('#tv').val()
            let occupation = $('#occupation').val()
            let monthlyCharge = $('#monthlyCharge').val()
            // let permanentDiscount = $('#permanentDiscount').val()

            let contextData = {
                name,
                fatherName,
                address,
                area,
                mobileNumber,
                nidNumber,
                connectionFee,
                tv,
                occupation,
                monthlyCharge,
                // permanentDiscount
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


    // previous bill updater function
    $(document).on('click', '.bill-update-btn', function () {
        let id = $(this).data('id')
        let billUpdateModal = $('#bill-update-modal')

        billUpdateModal.html(`<div class="modal-dialog" role="document">
                                <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="exampleModalLabel">পূর্বের বকেয়া সম্পদনা</h5>
                                
                                </div>
                                <div class="modal-body">
                                    <form class="form-inline justify-content-center">
                                    <div class="input-group mb-3">
                                        <div class="input-group-prepend">
                                        <span class="input-group-text">বকেয়ার পরিমান লিখুন</span>
                                        </div>
                                        <input class="form-control" id="bill-update-field" min="0" type="number">
                                    </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-danger" data-dismiss="modal">বাতিল</button>
                                    <button type="button" class="btn btn-primary">বিল তৈরী করুন</button>
                                </div>
                                </div>
                            </div>`)




        billUpdateModal.modal('show')
        billUpdateModal.find('.btn-primary').click(function () {
            billUpdateModal.find('.btn-danger').attr('disabled', true)
            $(this).html('<span class="spinner-border spinner-border-sm"></span>').attr('disabled', true)

            let preBillAmount = billUpdateModal.find('.form-control').val()
            if (preBillAmount != '' || preBillAmount != '0') {

                $.ajax({
                    method: 'post',
                    url: '/previous_bill_updater/' + id + '/',
                    dataType: 'json',
                    beforeSend: function (request) {
                        request.setRequestHeader('X-CSRFToken', csrftoken)
                    },
                    data: {
                        preDues: preBillAmount
                    },
                    success: function (data) {
                        console.log(data)
                        billUpdateModal.modal('hide')
                    },
                    error: function (error) {
                        console.log(error)
                    }
                })
            }

        })

    })






    // active inactive code here
    $(document).on('click', '.inactive-btn', function () {
        const inactiveBtn = $(this)
        let id = inactiveBtn.data('id')
        let isActive = inactiveBtn.data('isactive') == 'active' ? true : false
        let inactiveModal = $('#inactive-modal')

        inactiveModal.html(`<div class="modal-dialog modal-confirm">
                                    <div class="modal-content">
                                    <div class="modal-header flex-column">
                                        <div class="icon-box">
                                        <i class="fas fa-times"></i>
                                        </div>
                                        <h4 class="modal-title w-100"></h4>
                                        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="custom-control custom-checkbox">
                                        <input type="checkbox" class="custom-control-input" id="bill-confirm-btn">
                                        <label class="custom-control-label" for="bill-confirm-btn"></label>
                                        </div>
                                
                                    </div>
                                    <div class="modal-footer justify-content-center">
                                        <button type="button" class="btn btn-secondary" data-dismiss="modal">বাতিল</button>
                                        <button id="modal-inactive-btn" type="button" class="btn"></button>
                                    </div>
                                    </div>
                                </div>`)


        inactiveModal.modal('show')
        let modalIactiveButton = $('#modal-inactive-btn')
        let billConfirmButton = $("#bill-confirm-btn")



        // this action for Disconnections
        if (isActive) {
            inactiveModal.find('.icon-box').html('<i class="fas fa-times"></i>').removeClass('border-success')
            inactiveModal.find('.modal-title').html('এই গ্রাহককে বিচ্ছিন্ন করতে চান?')
            modalIactiveButton.html('বিচ্ছিন্ন করুন').addClass('btn-danger').removeClass('btn-success')
            billConfirmButton.next().html('<h5>এই মাসের বিলটি ডিলিট হবে?</h5>')
        } else {
            inactiveModal.find('.icon-box').html('<i class="fas fa-check text-success"></i>').addClass('border-success')
            inactiveModal.find('.modal-title').html('<span class="text-success">আপনি কি সচল করতে চান?</span>')
            modalIactiveButton.html('সচল করুন').addClass('btn-success').removeClass('btn-danger')
            billConfirmButton.next().html('<h5>এই মাসের বিল তৈরী হবে?</h5>')
        }


        modalIactiveButton.click(function () {

            context = {
                isActive: isActive,
                isBillDeleteOrGenerate: billConfirmButton.is(':checked')
            }


            $.ajax({
                beforeSend: function (request) {
                    request.setRequestHeader('X-CSRFToken', csrftoken)
                },
                method: 'POST',
                url: "/customers/" + id + '/inactive/',
                dataType: 'json',
                cache: true,
                data: context,
                success: function (data) {
                    inactiveModal.modal('hide')
                    console.log(data)
                    if (data.success) {
                        if (isActive) {
                            inactiveBtn
                                .addClass('btn-success')
                                .removeClass('btn-danger')
                                .html('<i class="fa fa-check"></i>')
                                .data('isactive', 'inactive')
                        } else {
                            inactiveBtn
                                .addClass('btn-danger')
                                .removeClass('btn-success')
                                .html('<i class="fa fa-times"></i>')
                                .data('isactive', 'active')

                        }
                    } else {
                        console.log(data)
                    }

                }
            })
        })
    })


    // Delete funtionality here 
    $(document).on('click', '.delete-btn', function () {
        // let id = $(this).data('id')


        const modal = $(`<div class="modal-dialog modal-confirm">
                            <div class="modal-content">
                            <div class="modal-header flex-column">
                                <div class="icon-box">
                                <i class="fas fa-times"></i>
                                </div>
                                <h4 class="modal-title w-100">আপনি কি নিশ্চিত?</h4>
                                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                            </div>
                            <div class="modal-body">
                                <p>আপনি কি সত্যিই এই গ্রাহককে মুছে ফেলতে চান? এই গ্রাহককে আর ফেরানো যাবে না।</p>
                            </div>
                            <div class="modal-footer justify-content-center">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">বাতিল</button>
                                <button id="modal-delete-btn" type="button" class=" btn btn-danger">ডিলিট করুন</button>
                            </div>
                            </div>
                        </div>`)



        const deleteBtn = $(this)
        const deleteModal = $('#delete-modal')
        deleteModal.html(modal)
        deleteModal.modal('show')

        $('#modal-delete-btn').click(function () {
            let id = deleteBtn.data('id')
            console.log(id)

            $.ajax({
                method: 'delete',
                url: '/api/customers/' + id + '/',
                beforeSend: function (request) {
                    request.setRequestHeader('X-CSRFToken', csrftoken)
                },
                success: function (data) {
                    deleteModal.modal('hide')
                    deleteBtn.parent().parent().remove()

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
                let condition = customer.isActive ? '<td class="text-light bg-success rounded px-2">সংযোগকৃত</td>' : '<td class="text-light bg-danger rounded">বিচ্ছিন্ন</td>'
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
                    //call sms check
                    sms_check()

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
            let txnId = $("#receipt").val();
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
    function sms_check() {
        $.get('/sms_check/', function (data) {
            let totalSms = Math.round((data.balance / data.rate) / 2)

            if (data.balance != 0) {
                $('#sms-balance').html(totalSms)
            } else {
                $('#sms-balance').html(`<a class='text-light' href='http://sms.greenweb.com.bd'>ক্লিক করুন</a> `)
                $('#sms').attr('disabled', true)
                $('#sms').attr('checked', false)
            }
        })
    }
})