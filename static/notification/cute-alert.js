// Alert box design by Igor Ferrão de Souza: https://www.linkedin.com/in/igor-ferr%C3%A3o-de-souza-4122407b/

const cuteAlert = ({
  type,
  title,
  message,
  img,
  buttonText = 'OK',
  confirmText = 'OK',
  vibrate = [],
  playSound = null,
  cancelText = 'Cancel',
  closeStyle,
}) => {
  return new Promise(resolve => {
    const existingAlert = document.querySelector('.alert-wrapper');

    if (existingAlert) {
      existingAlert.remove();
    }

    const body = document.querySelector('body');

    const scripts = document.getElementsByTagName('script');

    let src = '';

    for (let script of scripts) {
      if (script.src.includes('cute-alert.js')) {
        src = script.src.substring(0, script.src.lastIndexOf('/'));
      }
    }

    let btnTemplate = `
    <button class="alert-button ${type}-bg ${type}-btn">${buttonText}</button>
    `;

    if (type === 'question') {
      btnTemplate = `
      <div class="question-buttons">
        <button class="confirm-button ${type}-bg ${type}-btn">${confirmText}</button>
        <button class="cancel-button error-bg error-btn">${cancelText}</button>
      </div>
      `;
    }

    if (vibrate.length > 0) {
      navigator.vibrate(vibrate);
    }

    if (playSound !== null) {
      let sound = new Audio(playSound);
      sound.play();
    }

    const template = `
    <div class="alert-wrapper">
      <div  class="alert-frame">
        <span   class="alert-close ${
                   closeStyle === 'circle'
                     ? 'alert-close-circle'
                     : 'alert-close-default'
                 }">X</span>
         <span style="display:inline-block;width:35px;height:35px; border:1px solid  #5CB3FF; border-radius:40px; text-align:center; margin:10px; margin-top:-30px;padding:3px;background-color: #5CB3FF;">
         <i style="font-size:17pt;" class="ti-info"></i> </span>
         <b>Your feedback matters!</b>

        ${img !== '' ? '<div class="alert-header ' + type + '-bg" style="height:6px; border-radius:0px;background-color: #5CB3FF;" >' : '<div>'}
        </div>
        <div class="alert-body">
          <span class="alert-message">${message}</span>
            <div style='width:100%; text-align:center;'>

              <form style="display:inline-block; padding:0px; margin:0px; margin-top:-30px;" id="frmStarRating">
                  <fieldset class="starability-growRotate">
                      <legend></legend>
                      <input type="radio" id="no-rate" class="input-no-rate" name="rating" value="0" checked aria-label="No rating." />

                      <input type="radio" id="rate1" name="rating" value="1" />
                      <label for="rate1">1 star.</label>

                      <input type="radio" id="rate2" name="rating" value="2" />
                      <label for="rate2">2 stars.</label>

                      <input type="radio" id="rate3" name="rating" value="3" />
                      <label for="rate3">3 stars.</label>

                      <input type="radio" id="rate4" name="rating" value="4" />
                      <label for="rate4">4 stars.</label>

                      <input type="radio" id="rate5" name="rating" value="5" />
                      <label for="rate5">5 stars.</label>
                      <span class="starability-focus-ring"></span>
                  </fieldset>
              </form>
                  <textarea id="textualFeedback" style="width:100%; margin-bottom:20px;" cols="40" rows="5"></textarea>
            </div>


          ${btnTemplate}
        </div>
      </div>
    </div>
    `;

    body.insertAdjacentHTML('afterend', template);

    const alertWrapper = document.querySelector('.alert-wrapper');
    const alertFrame = document.querySelector('.alert-frame');
    const alertClose = document.querySelector('.alert-close');

    if (type === 'question') {
      const confirmButton = document.querySelector('.confirm-button');
      const cancelButton = document.querySelector('.cancel-button');

      confirmButton.addEventListener('click', () => {
        alertWrapper.remove();
        resolve('confirm');
      });

      cancelButton.addEventListener('click', () => {
        alertWrapper.remove();
        resolve();
      });
    } else {
      const alertButton = document.querySelector('.alert-button');

      alertButton.addEventListener('click', () => {
        sessionStorage.setItem("starRatingFeedback", getRadioVal(frmStarRating,"rating"));
        sessionStorage.setItem("textualFeedback", document.getElementById("textualFeedback").value);
        alertWrapper.remove();
        resolve('ok');
      });
    }

    alertClose.addEventListener('click', () => {
      alertWrapper.remove();
      resolve('close');
    });

/*     alertWrapper.addEventListener('click', () => {
      alertWrapper.remove();
      resolve();
    }); */

    alertFrame.addEventListener('click', e => {
      e.stopPropagation();
    });
  });
};

const cuteToast = ({ type, message, timer = 5000,  vibrate = [], playSound = null }) => {
  return new Promise(resolve => {
    const body = document.querySelector('body');

    const scripts = document.getElementsByTagName('script');

    let src = '';

    for (let script of scripts) {
      if (script.src.includes('cute-alert.js')) {
        src = script.src.substring(0, script.src.lastIndexOf('/'));
      }
    }

    let templateContainer = document.querySelector('.toast-container');

    if (!templateContainer) {
      body.insertAdjacentHTML(
        'afterend',
        '<div class="toast-container"></div>',
      );
      templateContainer = document.querySelector('.toast-container');
    }

    const toastId = id();

    const templateContent = `
    <div class="toast-content ${type}-bg" id="${toastId}-toast-content">
      <div>
        <div class="toast-frame">
          <div class="toast-body">
            
            ${img !== '' ? '<img class="toast-body-img" src="' + src + '/' + img + '" />' : ''}
            <div class="toast-body-content">
              <span class="toast-title">${title}</span>
              <span class="toast-message">${message}</span>
            </div>
            <div class="toast-close" id="${toastId}-toast-close">X</div>
          </div>
        </div>
        ${img !== '' ? '<div class="toast-timer ' + type + '-timer"  style="animation: timer' + timer + 'ms linear;>' : ''}
      </div>
    </div>
    `;

    const toasts = document.querySelectorAll('.toast-content');

    if (toasts.length) {
      toasts[0].insertAdjacentHTML('beforebegin', templateContent);
    } else {
      templateContainer.innerHTML = templateContent;
    }

    const toastContent = document.getElementById(`${toastId}-toast-content`);

    if (vibrate.length > 0) {
      navigator.vibrate(vibrate);
    }

    if (playSound !== null) {
      let sound = new Audio(playSound);
      sound.play();
    }

    setTimeout(() => {
      toastContent.remove();
      resolve();
    }, timer);

    const toastClose = document.getElementById(`${toastId}-toast-close`);

    toastClose.addEventListener('click', () => {
      toastContent.remove();
      resolve();
    });
  });
};

const id = () => {
  return '_' + Math.random().toString(36).substr(2, 9);
};

//---------------------------------------------------------------------

function getRadioVal(form, name) {
    var val;
    // get list of radio buttons with specified name
    var radios = form.elements[name];

    // loop through list of radio buttons
    for (var i=0, len=radios.length; i<len; i++) {
        if ( radios[i].checked ) { // radio checked?
            val = radios[i].value; // if so, hold its value in val
            break; // and break out of for loop
        }
    }
    return val; // return value of checked radio or undefined if none checked
}
//---------------------------------------------------------------------
function sendFeedback(type, query, user){

    var starRatingFeedback_1 =  sessionStorage.getItem("starRatingFeedback");
    var textualFeedback_1  =   sessionStorage.getItem("textualFeedback");

    var today = new Date();
    var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
    var dateTime = date+' '+time;

    cuteAlert({
      type: "info",
      title: "",
      message: "Please rate the research result:",
      buttonText: "Send"
    }).then(() => {

       var starRatingFeedback_2 =  sessionStorage.getItem("starRatingFeedback");
       var textualFeedback_2  =   sessionStorage.getItem("textualFeedback");

       if ((starRatingFeedback_1 !== starRatingFeedback_2) || (textualFeedback_1 !== textualFeedback_2)) {
            sendFeedbackToServer(type, dateTime, query, starRatingFeedback_2, textualFeedback_2, user);
            sessionStorage.setItem("starRatingFeedback","" );
            sessionStorage.setItem("textualFeedback", "");
       }
   });
}
//---------------------------------------------------------------------
function sendFeedbackToServer(type, time, query, star, description, user){
  newEntitiy={"type": type, "time": time, "query": query, "star": star, "description": description, "user": user};

  $.ajax({
    url: '../webSearch/sendFeedback',
    type: "POST",
    dataType: "json",
    data: JSON.stringify(newEntitiy),
  headers: {
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRFToken": getCookie("csrftoken"),  // don't forget to include the 'getCookie' function
  },
    success: (data) => {
      console.log(data);
    },
    error: (error) => {
      console.log(error);
    }
  });
}
//---------------------------------------------------------------------
