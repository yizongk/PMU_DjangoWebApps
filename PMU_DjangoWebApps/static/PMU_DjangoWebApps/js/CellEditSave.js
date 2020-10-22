// Written by Yi Zong Kuang
// Works well with well structured html table, with: table, thead, tbody, tr, td
// And for the attribute for the td: class, data-id, data-table, data-column

/* Use Instruction
    1. For any cells (td) that you want to edit add the following class to your td tag, like so:
        <td class="editable" >Some data here</td>            // This is for inputting direct values
        <td class="editable-select" >Some data here</td>     // This is for selecting from a list

        // =========================Examples=========================================
        <td class="editable"        data-id="{{ entry.user_permission_id }}" data-table="Users" data-column="Login">{{ entry.user.login }}</td>
        <td class="editable-select" data-id="{{ entry.user_permission_id }}" data-table="Users" data-column="Login">{{ entry.user.login }}</td>

    2. Then add the following js code (It's a template, change it to make it work for your use case)

        // =========================Examples=========================================
        //// ==========================For cell edit mode===============================

        $(document).on("dblclick", ".editable", function () {
            enterCellEditMode($(this))
        });

        $(document).on("keyup", ".input-data", function (e) {
            var key = e.which;
            if (key === 13) { // 13 is the return key, aka 'ENTER' key
                sendCellToServer(this, link_to_your_api, "input", function(td_node, json_response) {            // provide link_to_your_api, like "/PerInd/admin_panel_api_save_permission_data". And optionally, provide a call back function to do some work after the api call is successful
                    console.log(`Hi, call back called sendCellToServer(): ${json_response.post_msg}`)
                });
            }
            if (key === 27) { // 27 is the ESC key
                cancelEditMode(this);
            }
        });

        //// ==========================For cell select mode===============================

        $(document).on("dblclick", ".editable-select", function () {
            values_array = some_array                                                                           // provide values_array here, such as values_array = ["Option A", "Option B", "Option C"], or converting a python json obj to array: logins_array = {{ user_logins_json|safe }}
            // Move current select element to the top of the array
            var current_value = $(this).text()
            values_array.sort(function(x, y) {
                return x == current_value ? -1 : y == current_value ? 1 : 0;
            });
            enterCellEditSelectMode($(this), values_array)
        });

        $(document).on("keyup", ".input-data-select", function (e) {
            var key = e.which;
            if (key === 27) { // 27 is the ESC key
                cancelSelectMode(this);
            }
        });

        $(document).on("change", ".input-data-select", function () {
            sendCellToServer(this, link_to_your_api, "select", function(td_node, json_response) {               // provide link_to_your_api, like "/PerInd/admin_panel_api_save_permission_data". And optionally, provide a call back function to do some work after the api call is successful
                console.log(`Hi, call back called sendCellToServer(): ${json_response.post_msg}`)
            });
        });
*/





$(document).ajaxStart(function () {
    $("body").addClass("loading");
})
.ajaxStop(function () {
    $("body").removeClass("loading");
});

function setDatabaseStatus(good, msg) {
    // Set status light and error message to red and response error msg
    if (good == true) {
        $('.status_info.led_light').html("Database Status: <div class='led_green'></div>");
        $('.status_info.err_msg').html("");
    } else {
        $('.status_info.led_light').html("Database Status: <div class='led_red'></div>");
        $('.status_info.err_msg').html("Error: " + msg);
    }
};

function finishCellEditMode(td_node) {
    td_node.addClass("editable");
};

function finishCellSelectMode(td_node) {
    td_node.addClass("editable-select");
};

function enterCellEditMode(td_node) {
    var old_value = td_node.text();
    var input = "<input type='text' class='input-data' old_value='" + old_value + "' value='" + old_value + "' class='form-control'>";
    td_node.html(input);
    td_node.removeClass("editable");
};

// param selections is a array of strings that will populate the selection list
function enterCellEditSelectMode(td_node, selections) {
    var old_value = td_node.text();
    // var input = "<input type='text' class='input-data' value='" + old_value + "' class='form-control'>";

    var options = selections.map(function (each_select) {
        return `<option value='${each_select}'>${each_select}</option>`
    }).join('')
    var input = `
        <select class='input-data-select' old_value='${old_value}'>
            ${options}
        </select>
    `
    td_node.html(input);
    td_node.removeClass("editable-select");
};

function cancelEditMode(node) {
    var old_val = $(node).attr("value")
    var td_node = $(node).parent("td");
    td_node.html(old_val);
    finishCellEditMode(td_node);
};

function cancelSelectMode(node) {
    var old_val = $(node).attr("old_value")
    var td_node = $(node).parent("td");
    td_node.html(old_val);
    finishCellSelectMode(td_node);
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

// Sends a json blob to the api end point. Assumes the api end will know how to handle the json blob
// Expects a json obj in response, and must have the following variable "post_success" and "post_msg", ex. json_response["post_success"] and json_response["post_msg"]
// successCallbackFct and failCallbackFct's optional first param, must be the json_response obj. The success/fail fct can be used to do any work after the respective successful/fail api call, such as displaying a message etc
    // success/fail not as in server connectivity, but success as in connectivity is success, and successfuly processed the data. And failure as in connectivity is sucess but something prevented the server from processing the data in its functions.
    // For its optional 2nd param, it must be props, which contains some props in json form from the parent calling function
// ajaxFailCallbackFct is called when ajax fails because of connection issues, etc. The optional first param must be jqXHR. You can access jqXHR.status and jqXHR.responseText.
    // For its optional 2nd param, it must be props, which contains some props in json form from the parent calling function
// ajaxFailCallbackFct stores calling parent data that can be pass to the various callback function
function sentJsonBlobToApi( json_blob, api_url, successCallbackFct=function() { return; }, failCallbackFct=function() { return; }, ajaxFailCallbackFct=function() { return; }, props={} ) {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
            }
        }
    });

    $.ajax({
        url: api_url,
        type: "POST",
        data: JSON.stringify(json_blob),
        contentType: "application/json",
    })
    .done(function (json_response) {
        if (json_response["post_success"] == false) {
            console.log(`Error: Ajax calling '${api_url}'\nServer Response: ${json_response["post_msg"]}`);
            alert(`Something went wrong while trying to send form data to server.\nPlease contact ykuang@dot.nyc.gov if this error continues:\n\nAjax calling api endpoint: '${api_url}'\nServer Response:\n\n${json_response["post_msg"]}`);

            failCallbackFct(json_response, props)
            // Set status light and error message to red and response error msg
            setDatabaseStatus(good=false, msg=json_response["post_msg"]);
        } else { // Api call successful
            successCallbackFct(json_response, props);
            setDatabaseStatus(good=true, msg="");
        }

        return true;
    })
    .fail(function (jqXHR) {
        var errorMessage = `Server might be down, try to reload the web page to confirm. If error is still happening, contact ykuang@dot.nyc.gov\n xhr response: ${jqXHR.status}\n xhr response text: ${jqXHR.responseText}`;
        ajaxFailCallbackFct(jqXHR, props)
        setDatabaseStatus(good=false, msg=errorMessage);

        console.log(`Ajax Post: Error Occured: ${errorMessage}`);
        alert(`Ajax Post: Error Occured:\n\n${errorMessage}`);
        return false;
    });
}

function finishEditMode(td_node, cell_html_type) {
    if (cell_html_type == "input") {
        finishCellEditMode(td_node);
    } else if (cell_html_type == "select") {
        finishCellSelectMode(td_node)
    } else {
        console.log(`Warning: Unknown finish cell mode: ${cell_html_type}`)
    }
}

// THIS IS THE ENTRY POINT
// successCallbackFct must take in for its first param, the td_node, and then for its second param, the json_response obj. successCallbackFct can be used to do any work after a successful api call, such as updating some element on the html beside the new cell value (The new cell value is updated to the edited cell during the sendCellToServer() function).
// #@TODO refactor this to use the sentJsonBlobToApi() like sendModalFormDataToServer() and deleteRecordToServer()
function sendCellToServer( node, api_url, cell_html_type ) {
    // console.log(id, new_value, table, column, td_node, old_val);
    var old_val = $(node).attr("old_value")
    var new_value = $(node).val();
    var td_node = $(node).parent("td");
    $(node).remove();

    id = td_node.data("id")
    table = td_node.data("table")
    column = td_node.data("column")

    json_obj_to_server = {
        "id": id,
        "new_value": new_value,
        "table": table,
        "column": column
    }

    props = {
        'td_node': td_node,
        'old_val': old_val,
        'new_value': new_value,
        'cell_html_type': cell_html_type,
    }

    sentJsonBlobToApi( json_obj_to_server, api_url, function(json_response, props) {
        // successful api call call-back fct
        td_node = props['td_node']
        new_value = props['new_value']
        cell_html_type = props['cell_html_type']

        td_node.html(new_value);
        finishEditMode(td_node, cell_html_type)
    }, function(json_response, props) {
        // bad api call call-back fct
        td_node = props['td_node']
        old_val = props['old_val']
        cell_html_type = props['cell_html_type']

        td_node.html(old_val);
        finishEditMode(td_node, cell_html_type)
    },
    function(jqXHR, props) {
        // bad ajax call
        td_node = props['td_node']
        old_val = props['old_val']
        cell_html_type = props['cell_html_type']

        td_node.html(old_val);
        finishEditMode(td_node, cell_html_type)
    },
    props );

};

function sendModalFormDataToServer( json_blob, api_url, successCallbackFct=function() { return; }, failCallbackFct=function() { return; }, ajaxFailCallbackFct=function() { return; }, props={} ) {
    sentJsonBlobToApi(json_blob, api_url, successCallbackFct, failCallbackFct, ajaxFailCallbackFct, props);
};

function deleteRecordToServer( json_blob, api_url, successCallbackFct=function() { return; }, failCallbackFct=function() { return; }, ajaxFailCallbackFct=function() { return; }, props={} ) {
    sentJsonBlobToApi(json_blob, api_url, successCallbackFct, failCallbackFct, ajaxFailCallbackFct, props);
}