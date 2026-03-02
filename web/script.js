let lastImgData = null;
let currentButtonId = null;
let loaded_config = null;

window.onload = async () => {    
    await loadSavedConfig();
}

async function loadSavedConfig() {
    try {
        const [buttons, images, labels] = await eel.get_config()();

        loaded_config = buttons

        for (const [button_id, image_path] of Object.entries(images)) {
            await setButtonImage(button_id, image_path);
        }

        for (const [button_id, label_path] of Object.entries(labels)) {
            await setButtonLabel(button_id)
        }
        
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

async function setButtonImage(button_id, image_path) {
    const imgData = await eel.load_b64(image_path)();
    
    $("#"+button_id).css('background',`no-repeat center center url('${imgData}')`);
    $("#"+button_id).css('backgroundSize', 96 + 'px ' + 96 + 'px');
}

async function setButtonLabel(button_id) {
    const labelData = await eel.load_label(button_id)();

    if (!labelData) {
        return
    }

    $("#"+button_id.replace("btn", "txt")).attr('placeholder', labelData)
}

async function updateButtonDialog(button_id) {
    $(".btn").disabled = true
    $(".btn").css('cursor', 'default')
    $('#updateLabel').html('Aktualizacja przycisku: [' + button_id.slice(3) + "] (" + $("#"+button_id.replace("btn", 'txt')).attr('placeholder') + ")");
    $('#updateTxt').attr('placeholder', $("#"+button_id.replace("btn", 'txt')).attr('placeholder'));
    $('#updateBtn').css('background', $('#'+button_id).css('background'));
    $('#updateBtn').css('backgroundSize', 128 + 'px ' + 128 + 'px');
    $('#updatePopup').css('display', 'block');

    $(".rad").each(function(){
        $(this)[0].checked=false
    })

    if (loaded_config[button_id]) {
        switch (loaded_config[button_id].action_type) {
            case 'shortcut':
                $("#rad1")[0].checked = true;
                $("#sel1").css('display','block');
                $("#hotkeyInput").val(loaded_config[button_id].action_data)
                break;
            case 'txt':
                $("#rad2")[0].checked = true;
                $("#sel2").css('display','block');
                $("#macroInput").val(loaded_config[button_id].action_data)
                break;
            case 'program':
                $("#rad3")[0].checked = true;
                $("#sel3").css('display','block');
                $("#commandInput").val(loaded_config[button_id].action_data)
                break;
            default:
                break;
        }
    }
}

$('.btn').click(async (element) => {
    currentButtonId = element.target.id; 
    await updateButtonDialog(currentButtonId);
})

$('.rad').click((element) => {
    $('#sel1').css('display','none');
    $('#sel2').css('display','none');
    $('#sel3').css('display','none');

    $('#sel'+element.target.id[3]).css('display','block');
});

$('#backButton').click(async () => {
    currentButtonId = null;
    lastImgData = null;
    $('#updatePopup').css('display', 'none');

    $(".rad").each(function(){
        $(this)[0].checked=false
    })
    
    $('#sel1').css('display','none');
    $('#sel2').css('display','none');
    $('#sel3').css('display','none');
    
    $("#updateTxt").val("")
    $("#hotkeyInput").val("")
    $("#macroInput").val("")
    $("#commandInput").val("")

    $(".btn").disabled = false
    $(".btn").css('cursor', "pointer")

    await loadSavedConfig();
});

$('#updateBtn').click(async () => {
    input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/png,image/jpeg,image/jpg,image/bmp';
    
    input.onchange = e => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();   
            reader.onload = async function(e) {
                const imgData = e.target.result;
                $('#updateBtn').css('background', `white no-repeat center center url(${imgData})`);
                $('#updateBtn').css('backgroundSize', 96 + 'px ' + 96 + 'px');
                lastImgData = imgData;
            };
            reader.readAsDataURL(file);
        }
    };

    input.click();
});

$('#submit').click(async () => {
    const description = $('#updateTxt').val() || $('#updateTxt').attr('placeholder');
    
    $('#updatePopup').css('display', 'none');
    
    if (currentButtonId) {
        switch ($(".rad:checked")[0].id) {
            case "rad1":
                atype = "shortcut"
                action = $("#hotkeyInput").val()
                break
            case "rad2":
                atype = "txt"
                action = $("#macroInput").val()
                break
            case "rad3":
                atype = "program"
                action = $("#commandInput").val()
                break
        }

        if (lastImgData)
            await eel.save_button(currentButtonId, atype, action, description, lastImgData)()
        else
            try {
                lastImgData = await eel.load_b64(currentButtonId + ".jpg")();
                await eel.save_button(currentButtonId, atype, action, description, lastImgData)()
            } catch (error) {
                console.error('Error loading existing image:', error);
            }
        console.log(currentButtonId, atype, action, description, lastImgData)
        
        $('#'+currentButtonId).css('background', `white no-repeat center center url(${lastImgData})`);
        $('#'+currentButtonId).css('backgroundSize', 96 + 'px ' + 96 + 'px');
        
            
        const txtElement = $("#"+currentButtonId.replace("btn", "txt"));

        txtElement.attr('placeholder', description)
    }

    currentButtonId = null;
    lastImgData = null;

    $(".rad").each(function(){
        $(this)[0].checked=false
    })
    
    $('#sel1').css('display','none');
    $('#sel2').css('display','none');
    $('#sel3').css('display','none');
    
    $("#updateTxt").val("")
    $("#hotkeyInput").val("")
    $("#macroInput").val("")
    $("#commandInput").val("")
    
    $(".btn").disabled = false
    $(".btn").css('cursor', "pointer")

    await loadSavedConfig();
});

$('#delete').click(async () => {
    // $('#'+currentButtonId).css('background', 'none');
    // const txtElement = $("#"+currentButtonId.replace("btn", "txt"));
    // txtElement.attr('placeholder', "Opis funkcji")
    
    // $('#updatePopup').css('display', 'none');

    // $(".rad").each(function(){
    //     $(this)[0].checked=false
    // })
    
    // $('#sel1').css('display','none');
    // $('#sel2').css('display','none');
    // $('#sel3').css('display','none');
    
    // $("#updateTxt").val("")
    // $("#hotkeyInput").val("")
    // $("#macroInput").val("")
    // $("#commandInput").val("")
    
    // $(".btn").disabled = false
    // $(".btn").css('cursor', "pointer")

    await eel.clear_button()();

    // currentButtonId = null;
    // lastImgData = null;

    // await loadSavedConfig();
});



eel.expose(setConnection)
function setConnection(info) {
    if (info.connected==true) {
        $('#connectionIndicator').html("🟢");
        $('#connectionStatus').html("Connected to " + info.comport);
        // eel.overwrite_config()();
    } else {
        if (info.comport=='dropped') {
            $('#connectionIndicator').html("🟠");
            $('#connectionStatus').html("Connection dropped")
        } else {
            $('#connectionIndicator').html("🔴");
            $('#connectionStatus').html("Disconnected")
        }
    }
}

