function showFilterInput(elementid) {
    document.getElementById(elementid).style.display = "block";
    document.getElementById("formsubmitbutton").style.display = "block";
}
function filterSelection(value, rowvalue) {
    if (value == "Name") {
        document.getElementById("default").text = "Remove Filter";
        document.getElementById("personname").selected = true;
        document.getElementById("selectaddress").style.display = "none";
        document.getElementById("selectfamily").style.display = "none";
        document.getElementById("inputname").style.display = "block";
        document.getElementById("formsubmitbutton").style.display = "block";
        document.getElementById("namevalue").focus();
        if (rowvalue != "none"){
            count = (rowvalue.match(/%20/g) || []).length;
            for (let j = 0; j < count; j++) {
                rowvalue = rowvalue.replace("%20", " ");
            }
            document.getElementById("namevalue").value = rowvalue;
        }
    } else if (value == "Address") {
        document.getElementById("default").text = "Remove Filter";
        document.getElementById("address").selected = true;
        document.getElementById("inputname").style.display = "none";
        document.getElementById("selectfamily").style.display = "none";
        document.getElementById("selectaddress").style.display = "block";
        document.getElementById("formsubmitbutton").style.display = "block";
        for (let i = 0; i < document.getElementById("selectaddress").children.item(1).children.length; i++) {
            if (document.getElementById("selectaddress").children.item(1).children.item(i).value === rowvalue) {
                document.getElementById("selectaddress").children.item(1).children.item(i).selected = true;
            }
        }
    } else if (value == "FamilyName") {
        document.getElementById("default").text = "Remove Filter";
        document.getElementById("family").selected = true;
        document.getElementById("inputname").style.display = "none";
        document.getElementById("selectaddress").style.display = "none";
        document.getElementById("selectfamily").style.display = "block";
        document.getElementById("formsubmitbutton").style.display = "block";
        for (let i = 0; i < document.getElementById("selectfamily").children.item(1).children.length; i++) {
            if (document.getElementById("selectfamily").children.item(1).children.item(i).value === rowvalue) {
                document.getElementById("selectfamily").children.item(1).children.item(i).selected = true;
            }
        }
    } else {
        document.getElementById("default").text = "";
        document.getElementById("default").selected = true;
        document.getElementById("inputname").style.display = "none";
        document.getElementById("selectaddress").style.display = "none";
        document.getElementById("selectfamily").style.display = "none";
        document.getElementById("formsubmitbutton").style.display = "none";
        if (location.pathname != "/index") {
            location.pathname = "/index/filter/default/default";
        }
    }
}
function filteringOption() {
    if (document.getElementById("sorting").children.item(1).selected == true) {
        var rowvalue = document.getElementById("namevalue").value;
        if (rowvalue.length == 0) {
            document.getElementById("formsubmitbutton").children.item(0).href = "/index";
        } else {
            document.getElementById("formsubmitbutton").children.item(0).href = "/index/filter/Name/" + rowvalue;
        }
    } else if (document.getElementById("sorting").children.item(2).selected == true) {
        var rowvalue = document.getElementById("addressvalue").value;
        document.getElementById("formsubmitbutton").children.item(0).href = "/index/filter/Address/" + rowvalue;
    } else if (document.getElementById("sorting").children.item(3).selected == true) {
        var rowvalue = document.getElementById("familyvalue").value;
        document.getElementById("formsubmitbutton").children.item(0).href = "/index/filter/FamilyName/" + rowvalue;
    }
}
