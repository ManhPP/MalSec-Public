// Guacamole 1.5.x bridge. Keep version-coupled Angular access out of dashboard code.
// Guacamole must be reverse-proxied on the SAME origin as Malsec.
// Native contracts: guacamole-client/1.5.5 authenticationService (GUAC_AUTH)
// and ClientIdentifier (base64url of id + NUL + type + NUL + dataSource).
export function connectionUrl(url) {
  const parsed = new URL(url, window.location.href)
  parsed.hash = parsed.hash.split('?')[0]
  return parsed.href
}

export function guacamoleBase(url) {
  const parsed = new URL(url, window.location.href)
  if (parsed.origin !== window.location.origin) {
    throw new Error('Live VM previews require Guacamole on the same origin (for example /guacamole/).')
  }
  parsed.hash = ''
  parsed.search = ''
  return parsed.href
}

function injector(frame) {
  const win = frame?.contentWindow
  return win?.angular?.element(win.document.body).injector()
}

export async function bootstrapGuacamole(url, signal) {
  const data = new URLSearchParams(new URL(url, window.location.href).hash.split('?')[1]).get('data')
  if (!data) throw new Error('Missing Guacamole session credentials')
  // Authenticate BEFORE mounting any iframe. Otherwise Guacamole's own initial
  // token refresh can race this request or auto-open an old single connection.
  const response = await fetch(new URL('api/tokens', guacamoleBase(url)), {
    method: 'POST', signal, headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ data })
  })
  if (!response.ok) throw new Error(`Guacamole authentication failed (HTTP ${response.status}). Reload the VM session to retry.`)
  const auth = await response.json()
  if (!auth.authToken) throw new Error('Guacamole returned an invalid authentication result')
  if (!signal.aborted) {
    // Native Guacamole 1.5.x localStorageService stores AuthenticationResult
    // directly at GUAC_AUTH. Do not clear unrelated storage or revoke tokens
    // still used by an already open external window.
    window.localStorage.setItem('GUAC_AUTH', JSON.stringify(auth))
  }
}

export function mirrorGuacamole(frame, canvas, url) {
  const services = injector(frame)
  if (!services) return 'Connecting…'
  const id = new URL(connectionUrl(url)).hash.replace('#/client/', '')
  const clients = services.get('guacClientManager').getManagedClients()
  const managed = clients[id]
  if (!managed) return 'Connecting…'
  const state = managed.clientState.connectionState
  if (state !== 'CONNECTED') return state === 'CONNECTING' ? 'Connecting…' : state
  const display = managed.client.getDisplay().flatten()
  const context = canvas.getContext('2d')
  context.fillStyle = '#090d16'
  context.fillRect(0, 0, canvas.width, canvas.height)
  if (display.width && display.height) {
    const scale = Math.min(canvas.width / display.width, canvas.height / display.height)
    const width = display.width * scale, height = display.height * scale
    context.drawImage(display, (canvas.width - width) / 2, (canvas.height - height) / 2, width, height)
  }
  return 'Connected'
}
