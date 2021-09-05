function showFamilyOtherInput() {
    thist = document.getElementById("familynames");
    if (thist.options[thist.selectedIndex].text == "Other") {
        document.getElementById("familyotherinput").style.display = "block";
    } else {
        document.getElementById("familyotherinput").style.display = "none";
    }
}
function eraseoptions(elementid, check) {
    var options = document.getElementById(elementid);
    i = 1;
    while (i < options.length) {
        options.removeChild(options.lastElementChild);
    }
    if (elementid === "selectcity" && check ==="1") {
        var a = document.createElement("option");
        a.setAttribute("value", "");
        a.innerHTML = "Select State";
        options.appendChild(a);
    }
}
function showState() {
    stateslist = document.getElementById("stateslist").value;
    eraseoptions("selectstate", "2");
    eraseoptions("selectcity", "1");
    thist = document.getElementById("selectcountry");
    var country = thist.options[thist.selectedIndex].value;
    var countryid = country.split(" | ")[1];
    var states = stateslist.split("[");
    for (let i = 2; i < states.length; i++) {
        var coloumns = states[i].replace("],",'').split(",");
        if (coloumns[0] == countryid) {
            var statename = coloumns[2].replace("'","");
            var statename = statename.replace("'","");
            var statevalue = [statename, "|", coloumns[1]];
            var x = document.createElement("option");
            x.setAttribute("value", statevalue.join(""));
            var z = document.createTextNode(statename);
            x.appendChild(z);
            document.getElementById("selectstate").appendChild(x);
        }
    }
}
function showCity() {
    citieslist = document.getElementById("citieslist").value;
    eraseoptions("selectcity", "2");
    thist = document.getElementById("selectstate");
    var state = thist.options[thist.selectedIndex].value;
    var stateid = state.split(" | ")[1];
    var cities = citieslist.split("[");
    for (let i = 2; i < cities.length; i++) {
        var coloumns = cities[i].replace("],",'').split(",");
        if (coloumns[0] == stateid) {
            var cityname = coloumns[2].replace("'","");
            var cityname = cityname.replace("'","");
            var x = document.createElement("option");
            x.setAttribute("value", cityname);
            var z = document.createTextNode(cityname);
            x.appendChild(z);
            document.getElementById("selectcity").appendChild(x);
        }
    }
}
function showPhoneInput(phonenumber) {
    if (phonenumber != undefined) {
        var phonenum = phonenumber.split(" ");
    }
    var phonecodelist = document.getElementById("phonecodelist").value;
    var anotherphone = document.getElementById("phone");
    var lastelement = anotherphone.children.length;
    var rowdiv = document.createElement("div");
    var predivid = document.getElementById("phone").children.item(lastelement-1).getAttribute("id").replace("extraphone", "");
    var nowdivid = Number(predivid) + 1;
    divid = "extraphone" + String(nowdivid);
    rowdiv.setAttribute("id", divid);
    rowdiv.setAttribute("class", "row");
    rowdiv.setAttribute("style", "margin: 0px;")
    anotherphone.appendChild(rowdiv);
    /**/
    var select = document.createElement("select");
    select.setAttribute("class", "col-10");
    select.setAttribute("style", "padding-right: 0px; padding-left: 0px; font-size: small; margin-top: 2px; margin-bottom: 2px;");
    anotherphone.children.item(lastelement).appendChild(select);
    /**/
    var phonecode = phonecodelist.split("[").slice(2);
    for (let i = 0; i < 250; i++) {
        var phonedet = phonecode[i].split(", ").slice(1);
        var phone = phonedet[1].replace("'","")
        var phone = phone.replace("']","")
        var phonecount = phonedet[0].replace("'","")
        var phonecount = phonecount.replace("'","")
        var option = document.createElement("option");
        option.setAttribute("value", phone);
        if (phonenumber != undefined && phone == phonenum[0]) {
            var indextoselect = i;
        }
        option.innerHTML = phone + " " + phonecount;
        anotherphone.children.item(lastelement).children.item(0).appendChild(option);
    }
    if (phonenumber == undefined) {
        anotherphone.children.item(lastelement).children.item(0).options[102].selected = true;
    } else {
        anotherphone.children.item(lastelement).children.item(0).options[indextoselect].selected = true;
    }
    /**/
    var input = document.createElement("INPUT");
    input.setAttribute("type", "tel");
    input.setAttribute("class", "col-30");
    input.setAttribute("pattern", "[0-9]{[0-20]}");
    input.setAttribute("title", "Enter only numbers")
    input.setAttribute("style", "padding: 5px");
    if (phonenumber != undefined) {
        input.setAttribute("value", phonenum[1]);
    }
    input.setAttribute("required", "");
    anotherphone.children.item(lastelement).appendChild(input);
    /**/
    if (phonenumber == undefined || lastelement > 2) {
        var deletebutton = document.createElement("button");
        deletebutton.setAttribute("onclick", "deletePhone("+divid+")")
        deletebutton.setAttribute("class", "btn btn-default");
        deletebutton.setAttribute("style", "border-color: transparent")
        deletebutton.setAttribute("data-toggle", "tab");
        deletebutton.innerHTML = "X";
        anotherphone.children.item(lastelement).appendChild(deletebutton);
    }
}
function deletePhone(divid) {
    divid.remove();
}
function phoneNumberCollect() {
    var phoneParent = document.getElementById("phone");
    var last = phoneParent.children.length;
    var combinedphone = phoneParent.children.item(2).children.item(0).value + " " + phoneParent.children.item(2).children.item(1).value;
    if (last > 2) {
        for (let i = 3; i < last; i++) {
            combinedphone = combinedphone + ", " + phoneParent.children.item(i).children.item(0).value + " " + phoneParent.children.item(i).children.item(1).value;
        }
    }
    document.getElementById("phone").children.item(1).children.item(0).value = combinedphone;
}
