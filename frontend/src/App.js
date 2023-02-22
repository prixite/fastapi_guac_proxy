import { useRef } from "react";
import Guacamole from "guacamole-common-js";

import "./App.css";

function App() {
  const client = useRef();

  const disconnect = () => {
    client.current.disconnect();
  };

  const connect = () => {
    const hostname = document.getElementById("guacd-host").value;
    const port = document.getElementById("guacd-port").value;
    const protocol = document.getElementById("protocol").value;
    const remoteHost = document.getElementById("remote-host").value;
    const remotePort = document.getElementById("remote-port").value;
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const tunnel = new Guacamole.WebSocketTunnel(
      "ws://localhost:8000/websocket/"
    );
    const guac = client.current = new Guacamole.Client(tunnel);
    document
      .getElementById("display")
      .appendChild(guac.getDisplay().getElement());

    guac.connect([
      `guacd_host=${hostname}`,
      `guacd_port=${port}`,
      `protocol=${protocol}`,
      `remote_host=${remoteHost}`,
      `remote_port=${remotePort}`,
      `username=${username}`,
      `password=${password}`,
    ].join("&"));

    window.onunload = function() {
      guac.disconnect();
    }

    // Mouse
    var mouse = new Guacamole.Mouse(guac.getDisplay().getElement());

    mouse.onmousedown =
      mouse.onmouseup   =
      mouse.onmousemove = function(mouseState) {
        guac.sendMouseState(mouseState);
      };

    // Keyboard
    var keyboard = new Guacamole.Keyboard(document);

    keyboard.onkeydown = function (keysym) {
      guac.sendKeyEvent(1, keysym);
    };

    keyboard.onkeyup = function (keysym) {
      guac.sendKeyEvent(0, keysym);
    };
  };

  return (
    <>
      <div>
        <div>
          <label>
            Guacd Server Hostname:
            <input id="guacd-host" type="text" defaultValue={"74.207.234.105"} />
          </label>
        </div>
        <div>
          <label>
            Guacd Server Port:
            <input id="guacd-port" type="text" defaultValue={"4822"} />
          </label>
        </div>
        <div>
          <label>
            Connection Type:
            <select id="protocol">
              <option value="vnc">VNC</option>
              <option value="ssh">SSH</option>
              <option value="rdp">RDP</option>
            </select>
          </label>
        </div>
        <div>
          <label>
            Remote Server Hostname:
            <input type="text" id="remote-host" />
          </label>
        </div>
        <div>
          <label>
            Remote Server Port:
            <input type="text" id="remote-port" />
          </label>
        </div>
        <div>
          <label>
            Username:
            <input type="text" id="username" />
          </label>
        </div>
        <div>
          <label>
            Password:
            <input type="password" id="password" />
          </label>
        </div>
        <button onClick={connect}>Connect</button>
        <button onClick={disconnect}>Disconnect</button>
      </div>
      <div id="display"></div>
    </>
  );
}

export default App;
