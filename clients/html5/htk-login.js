/*
 date: 25/01/2021
 author: Luca Porzio

 copyright: Copyright 2017 F4E | European Joint Undertaking for ITER and
 the Development of Fusion Energy ('Fusion for Energy').
 Licensed under the EUPL, Version 1.1 or - as soon they will be approved
 by the European Commission - subsequent versions of the EUPL (the "Licence")
 You may not use this work except in compliance with the Licence.
 You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

 warning: Unless required by applicable law or agreed to in writing,
 software distributed under the Licence is distributed on an "AS IS"
 basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 or implied. See the Licence permissions and limitations under the Licence.
-*/
      //  <link rel="import" href="/htk-helper.html">
      import HtkHelper from './htk-helper.js'

        const template = document.createElement('template');
        template.innerHTML = `
          <dialog id="dlogin">
              <div id="divlogin">
                  <table style="border-style:solid;border-width:1px;width: 100%">
                      <tr>
                          <td><label for="username">User:</label></td>
                          <td><input type="text" id="username"></input></td>
                      </tr>
                      <tr>
                          <td><label for="password">Password:</label></td>
                          <td><input type="password" id="password"></input></td>
                      </tr>
                  </table>
                  <table style="border-style:solid;border-width:0px;width: 100%">
                      <tr>
                          <td style="padding-top:20px;">
                              <button title="Login" id="loginbtn">Login</button>
                              <button title="Cancel" id="cancelbtn">Cancel</button>
                          </td>
                      </tr>
                  </table>
              </div>
          </dialog>
        `;


  /**
   * @brief A login dialog.
   */
  export class HtkLogin extends HTMLElement {

      /**
       * @brief Constructor. NOOP.
       */
      constructor() {
          super();
      }

      /**
       * @brief Register the components
       */
      connectedCallback () {
          var templateContent = template.content;
          // import template into
          const root = this.attachShadow({mode: 'open'});
          root.appendChild(templateContent.cloneNode(true));

          this.diag = this.shadowRoot.querySelector("#dlogin");
          this.loginDiv = this.shadowRoot.querySelector("#divlogin");
          var loginButton = this.shadowRoot.querySelector("#loginbtn");
          loginButton.onclick = function() {
              var usernameTxt = this.shadowRoot.querySelector("#username");
              var passwordTxt = this.shadowRoot.querySelector("#password");
              HtkHelper.loginToServer(
                  usernameTxt.value,
                  passwordTxt.value,
                  function(user) {
                      localStorage.user = JSON.stringify(user);
                      HtkHelper.setToken(user.token);
                      this.fireLoginSuccessful(user);
                      if (this.diag.open) {
                          this.diag.close();
                      }
                  }.bind(this),
                  function() {
                      alert("Login failed!");
                  }
              );
          }.bind(this);

          var cancelButton = this.shadowRoot.querySelector("#cancelbtn");
          cancelButton.onclick = function() {
              this.diag.close();
          }.bind(this);

          this.loginListeners = [];
      }

      /**
       * @brief Warns all the registered listeners that a user has been successfully logged into the system.
       * @param[in] user the user that was logged into the system.
       */
      fireLoginSuccessful(user) {
          for(var l in this.loginListeners) {
              this.loginListeners[l].loginSuccessful(user);
          }
      }

      /**
       * @brief Register a component to listen for login events.
       * @param[in] comp the component to register.
       */
      addLoginListener(comp) {
          this.loginListeners.push(comp);
      }

      /**
       * @brief Shows the login dialog.
       */
      show() {
          this.diag.showModal();
      }
  }

  /**
   * @brief Registers the element.
   */
  customElements.define('htk-login', HtkLogin);
