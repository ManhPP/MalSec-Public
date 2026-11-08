import React, { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { bootstrapGuacamole, connectionUrl, guacamoleBase, mirrorGuacamole } from '../lib/guacamole'

// A thumbnail is a canvas mirror, NOT another remote connection. Switching only
// changes iframe position; it never changes src, parent, key or guest resolution.
export default function GuacamoleWorkspace({ sessions, activeId, onSelect, activeFrameRef, thumbnailContainer }) {
  const frames = useRef(new Map())
  const canvases = useRef(new Map())
  const [ready, setReady] = useState(false)
  const [error, setError] = useState('')
  const [states, setStates] = useState({})
  const first = sessions[0]
  const firstUrl = first?.guacamole_url
  let base = ''
  let originError = ''
  try { if (firstUrl) base = guacamoleBase(firstUrl) } catch (err) { originError = err.message }

  useEffect(() => {
    const controller = new AbortController()
    setReady(false)
    setError('')
    if (!base || !first) return () => controller.abort()
    bootstrapGuacamole(firstUrl, controller.signal)
      .then(() => { if (!controller.signal.aborted) setReady(true) })
      .catch(err => { if (!controller.signal.aborted) setError(err.message || 'Guacamole authentication failed') })
    return () => controller.abort()
  }, [firstUrl, base])

  useEffect(() => {
    activeFrameRef.current = frames.current.get(activeId) || null
    activeFrameRef.current?.contentWindow?.focus()
    return () => { activeFrameRef.current = null }
  }, [activeId, ready, activeFrameRef])

  useEffect(() => {
    if (!ready) return
    const timer = setInterval(() => {
      const next = {}
      sessions.forEach(vm => {
        const frame = frames.current.get(vm.lab_vm_id), canvas = canvases.current.get(vm.lab_vm_id)
        if (!frame || !canvas) return
        try { next[vm.lab_vm_id] = mirrorGuacamole(frame, canvas, vm.guacamole_url) }
        catch { next[vm.lab_vm_id] = 'Live preview unavailable' }
      })
      setStates(next)
    }, 750)
    return () => clearInterval(timer)
  }, [sessions, ready])

  return (
    <>
      <div style={{ width: '100%', height: '100%', flex: 1, minHeight: 0, position: 'relative', overflow: 'hidden', background: '#090d16' }}>
        {(originError || error) && <div role="alert" style={{ padding: 20, color: 'var(--neon-ruby)' }}>{originError || error}</div>}
        {!ready && !error && !originError && <div role="status" style={{ padding: 20, color: 'var(--text-secondary)' }}>Authorizing lab desktops…</div>}
        {!originError && ready && sessions.map((vm, index) => (
          <iframe
            key={`${vm.lab_vm_id}:${vm.guacamole_url}`}
            ref={element => { if (element) frames.current.set(vm.lab_vm_id, element); else frames.current.delete(vm.lab_vm_id) }}
            src={connectionUrl(vm.guacamole_url)}
            title={`Lab VM ${index + 1} — ${vm.vmid}`}
            tabIndex={vm.lab_vm_id === activeId && ready ? 0 : -1}
            aria-hidden={vm.lab_vm_id !== activeId || !ready}
            allow="clipboard-read; clipboard-write; fullscreen; keyboard-map"
            style={{ position: 'absolute', width: '100%', height: '100%', border: 0,
              left: vm.lab_vm_id === activeId && ready ? 0 : -10000,
              top: 0,
              pointerEvents: vm.lab_vm_id === activeId && ready ? 'auto' : 'none' }}
          />
        ))}
      </div>
      {/* Only the thumbnails move outside the desktop frame; iframes stay here. */}
      {thumbnailContainer && createPortal(
        <div role="tablist" aria-label="Lab machines" onMouseEnter={e => e.stopPropagation()} onClick={e => e.stopPropagation()}
          style={{ display: 'flex', gap: 8, padding: 8, overflowX: 'auto', border: '1px solid var(--border-color)', borderRadius: 8, background: 'var(--bg-secondary)' }}>
          {sessions.map((vm, index) => (
            <button key={vm.lab_vm_id} type="button" role="tab" aria-selected={activeId === vm.lab_vm_id}
              onClick={() => onSelect(vm.lab_vm_id)} className="btn btn-secondary"
              style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: 5, flexShrink: 0,
                borderColor: activeId === vm.lab_vm_id ? 'var(--neon-cyan)' : 'var(--border-color)' }}>
              <canvas ref={element => { if (element) canvases.current.set(vm.lab_vm_id, element); else canvases.current.delete(vm.lab_vm_id) }}
                width={192} height={108} style={{ width: 144, height: 81, background: '#090d16' }} />
              <span style={{ fontSize: 12 }}>Machine {index + 1} · VM {vm.vmid}</span>
              <span style={{ fontSize: 10, color: 'var(--text-secondary)' }}>{states[vm.lab_vm_id] || 'Connecting…'}</span>
            </button>
          ))}
        </div>,
        thumbnailContainer
      )}
    </>
  )
}
