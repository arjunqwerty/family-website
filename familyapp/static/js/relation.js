function selectoption(eleid, rowval) {
    var selectopt = document.getElementById(eleid);
    var count = 0;
    for (let i = 0; i < selectopt.length; i++) {
        if (selectopt.options[i].value == rowval) {
            selectopt.options[i].selected = true;
            count += 1;
        }
    }
    if (count == 0 && rowval != "") {
        var x = document.createElement("option");
        x.setAttribute("value", rowval);
        x.innerHTML = rowval;
        x.setAttribute("selected", "");
        selectopt.appendChild(x);
    }
}
function selectmultioption(eleid, rowval) {
    var rowlist = rowval.split(", ");
    var parentdiv = document.getElementById(eleid);
    for (let i = 0; i < rowlist.length; i++) {
        var selectid = eleid.slice(0,-3) + "name" + String(Number(parentdiv.children.item(parentdiv.children.length-1).id.slice(-1)) + 1);
        var otherdiv = document.createElement("div");
        otherdiv.setAttribute("id", selectid);
        parentdiv.appendChild(otherdiv);
        var select = document.createElement("select");
        select.setAttribute("id", "select" + selectid);
        select.setAttribute("style", "width: 80%; padding: 5px;");
        select.setAttribute("onchange", "otherInput.call(this, event, '" + selectid + "')");
        select.setAttribute("required", "");
        document.getElementById(selectid).appendChild(select);
        var lastselect = parentdiv.children.item(parentdiv.children.length - 1).children.item(0);
        var opt = document.createElement("option");
        opt.setAttribute("value", " ");
        opt.innerHTML = "Select";
        lastselect.appendChild(opt);
        var lstname = nameslist();
        for (let j = 0; j < lstname.length; j++) {
            var option = document.createElement("option");
            option.setAttribute("value", lstname[j]);
            option.innerHTML = lstname[j];
            lastselect.appendChild(option);
        }
        var opti = document.createElement("option");
        opti.setAttribute("value", "None");
        opti.innerHTML = "None";
        lastselect.appendChild(opti);
        var optii = document.createElement("option");
        optii.setAttribute("value", "Other");
        optii.innerHTML = "Other";
        lastselect.appendChild(optii);
        selectoption("select" + selectid, rowlist[i]);
        if (rowval == '') {
            var deletebutton = document.createElement("button");
            deletebutton.setAttribute("onclick", "deleteOtherInput('"+selectid+"', '')");
            deletebutton.setAttribute("class", "btn btn-default");
            deletebutton.setAttribute("style", "border-color: transparent");
            deletebutton.setAttribute("data-toggle", "tab");
            deletebutton.innerHTML = "X";
            document.getElementById(selectid).appendChild(deletebutton);
        }
    }
}
function otherInput(event, elementid) {
    if (this.options == undefined || this.options[this.selectedIndex].text == "Other") {
        var parentdiv = document.getElementById(elementid).parentElement;
        if (this.options != undefined) {
            document.getElementById(elementid).style.display = "none";
        }
        var otherinputid = elementid.slice(0,-1) + String(Number(parentdiv.children.item(parentdiv.children.length-1).id.slice(-1)) + 1);
        var otherdiv = document.createElement("div");
        otherdiv.setAttribute("id", otherinputid);
        parentdiv.appendChild(otherdiv);
        var otherinput = document.createElement("input");
        otherinput.setAttribute("name", otherinputid);
        otherinput.setAttribute("style", "width: 80%;");
        document.getElementById(otherinputid).appendChild(otherinput);
        var deletebutton = document.createElement("button");
        if (this.options == undefined) {
            deletebutton.setAttribute("onclick", "deleteOtherInput('"+otherinputid+ "', '')");
        } else {
            deletebutton.setAttribute("onclick", "deleteOtherInput('"+otherinputid+ "', '" + elementid+"')");
        }
        deletebutton.setAttribute("class", "btn btn-default");
        deletebutton.setAttribute("style", "border-color: transparent");
        deletebutton.setAttribute("data-toggle", "tab");
        deletebutton.innerHTML = "X";
        document.getElementById(otherinputid).appendChild(deletebutton);
    }
}
function deleteOtherInput(otherinp, eleid) {
    if (eleid != '') {
        document.getElementById(eleid).style.display = "block";
    }
    document.getElementById(otherinp).remove();
}
function nameslist() {
    var lst = document.getElementById("allperson").value.replace("[('", "");
    lst = lst.replace("',)]", "");
    nameslst = lst.split("',), ('");
    return nameslst;
}
function checkOtherValue(elementid) {
    var parentdiv = document.getElementById(elementid).parentElement;
    if (parentdiv.children.item(1).value == "Other") {
        var anotheroption = document.createElement("option");
        anotheroption.setAttribute("value", parentdiv.children.item(2).children.item(0).value);
        anotheroption.setAttribute("selected", "");
        document.getElementById(elementid).appendChild(anotheroption);
    }
}
function collectChildSibling() {
    checkOtherValue("spousename0");
    checkOtherValue("fathername0");
    checkOtherValue("mothername0");
    var child = document.getElementById("childrendiv");
    var childvalue = child.children.item(2).children.item(0).value;
    for (let i = 3; i < child.children.length; i++) {
        if (child.children.item(i).children.item(0).value != "Other") {
            childvalue = childvalue + ", " + child.children.item(i).children.item(0).value;
        }
    }
    childvalue = childvalue.replace("Other, ", "");
    child.children.item(0).value = childvalue;
    var sibling = document.getElementById("siblingdiv");
    var siblingvalue = sibling.children.item(2).children.item(0).value;
    for (let i = 3; i < sibling.children.length; i++) {
        if (sibling.children.item(i).children.item(0).value != "Other") {
            siblingvalue = siblingvalue + ", " + sibling.children.item(i).children.item(0).value;
        }
    }
    siblingvalue = siblingvalue.replace("Other, ", "");
    sibling.children.item(0).value = siblingvalue;
}
