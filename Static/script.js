      // ── Helpers ──────────────────────────────────────────────
      function showToast(msg, duration = 2800) {
        const t = document.getElementById('toast');
        t.textContent = msg;
        t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), duration);
      }

      function getInitials(name) {
        return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
      }

      // ── Display Name ─────────────────────────────────────────
      function Display_name() {
        const name = "{{name}}";
        document.getElementById('nameEl').textContent = name;
        document.getElementById('avatarEl').textContent = getInitials(name);
      }
      Display_name();

      // ── Date chip ────────────────────────────────────────────
      document.getElementById('datechip').textContent = new Date().toLocaleDateString('en-IN', {
        weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
      });

      // ── Check-in ─────────────────────────────────────────────
      function checkIn() {
        if (!navigator.geolocation) { alert('Geolocation not supported'); return; }
        navigator.geolocation.getCurrentPosition(
          async function (position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            try {
              const geoRes  = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`);
              const geoData = await geoRes.json();
              const location_name = geoData.display_name;

              const data = {
                user_id: "{{ user_id }}",
                name: "{{name}}",
                lat: lat,
                lng: lng,
                location_name: location_name,
              };

              const res = await fetch('/checkin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
              });
              const result = await res.json();
              showToast(result.message || 'Checked in successfully');
            } catch (err) {
              showToast('Check-in failed. Please try again.');
            }
          },
          function () { alert('Location access denied'); }
        );
      }

      // ── Check-out ────────────────────────────────────────────
      function checkout() {
        if (!navigator.geolocation) { alert('Geolocation not supported'); return; }
        navigator.geolocation.getCurrentPosition(
          async function (position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            try {
              const geoRes  = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`);
              const geoData = await geoRes.json();
              const location_name = geoData.display_name;

              const data = {
                user_id: "{{ user_id }}",
                lat: lat,
                lng: lng,
                location_name: location_name,
              };

              const res = await fetch('/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
              });
              const result = await res.json();
              showToast(result.message || 'Checked out successfully');
            } catch (err) {
              showToast('Check-out failed. Please try again.');
            }
          },
          function () { alert('Location access denied'); }
        );
      }

      // ── View Attendance ───────────────────────────────────────
      function viewAttendance() {
        const tbody = document.getElementById('attendanceBody');
        tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state">Loading records…</div></td></tr>`;

        fetch('/view_attendance', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: "{{ user_id }}", name: "{{name}}" }),
        })
          .then(res => res.json())
          .then(data => {
            if (!data || data.length === 0) {
              tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state">No attendance records found.</div></td></tr>`;
              return;
            }

            // Compute summary metrics
            const presentDays = data.filter(r => r.status && r.status.toLowerCase() === 'present').length;
            const onTime      = data.filter(r => r.status && ['present','half day'].includes(r.status.toLowerCase())).length;
            const rate        = data.length > 0 ? Math.round((onTime / data.length) * 100) : 0;

            // Parse working hours (expects "Xh Ym" or decimal string)
            let totalHours = 0, countHours = 0;
            data.forEach(r => {
              if (r.Working_hours && r.Working_hours !== '—') {
                const hMatch = String(r.Working_hours).match(/(\d+(\.\d+)?)/);
                if (hMatch) { totalHours += parseFloat(hMatch[1]); countHours++; }
              }
            });
            const avgHours = countHours > 0 ? (totalHours / countHours).toFixed(1) : '—';

            document.getElementById('metricPresent').textContent = presentDays;
            document.getElementById('metricHours').textContent   = avgHours;
            document.getElementById('metricRate').innerHTML      = rate + '<span>%</span>';

            // Badge map
            const badgeMap = {
              present:  `<span class="badge badge-present"><span class="dot dot-present"></span>Present</span>`,
              absent:   `<span class="badge badge-absent"><span class="dot dot-absent"></span>Absent</span>`,
              late:     `<span class="badge badge-late"><span class="dot dot-late"></span>Late</span>`,
              'half day': `<span class="badge badge-half"><span class="dot dot-half"></span>Half day</span>`,
            };

            tbody.innerHTML = data.map(r => {
              const statusKey = (r.status || '').toLowerCase();
              const badge = badgeMap[statusKey] || `<span class="badge badge-absent">${r.status || '—'}</span>`;
              return `<tr>
                <td>${r.date || '—'}</td>
                <td class="mono">${r.check_in || '—'}</td>
                <td class="mono">${r.check_out || '—'}</td>
                <td class="mono">${r.Working_hours || '—'}</td>
                <td>${badge}</td>
              </tr>`;
            }).join('');
          })
          .catch(() => {
            tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state">Failed to load records.</div></td></tr>`;
          });
      }
