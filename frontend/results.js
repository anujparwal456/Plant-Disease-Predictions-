// Load scan result
function loadResults() {
  const data = sessionStorage.getItem("scanResult")

  if (!data) {
    window.location.href = "index.html"
    return
  }

  const result = JSON.parse(data)

  // Set image
  document.getElementById("resultImage").src = result.image

  // Set status bar color
  const statusBars = document.querySelectorAll(".status-bar")
  statusBars.forEach((bar) => {
    if (result.status !== "healthy") {
      bar.classList.add("diseased")
    }
  })

  // Set quick stats
  document.getElementById("statConfidence").textContent = `${result.confidence}%`

  const severityElement = document.getElementById("statSeverity")
  severityElement.textContent = result.severity
  if (result.severity === "None") {
    severityElement.style.color = "#16a34a"
  } else if (result.severity.includes("Moderate")) {
    severityElement.style.color = "#ea580c"
  } else {
    severityElement.style.color = "#dc2626"
  }

  document.getElementById("statSpread").textContent = result.spreadRisk.split("-")[0].trim()
  document.getElementById("statRecovery").textContent = result.estimatedRecovery.split(",")[0]

  // Set scan info
  document.getElementById("scanDate").textContent = new Date(result.scanDate).toLocaleString()
  document.getElementById("reportId").textContent = `Report ID: ${result.id}-${Date.now()}`

  // Determine flagged state based on low confidence or other warnings
  const hasLowConfidence = result.report && result.report.low_confidence_warning
  const isFlagged = result.uncertain || result.ambiguous || hasLowConfidence

  // Set disease identification
  const statusIcon = document.getElementById("statusIcon")
  if (isFlagged) {
    statusIcon.setAttribute("data-lucide", "alert-triangle")
    statusIcon.style.color = "#b45309"
  } else {
    statusIcon.setAttribute("data-lucide", result.status === "healthy" ? "check-circle-2" : "alert-circle")
    statusIcon.style.color = result.status === "healthy" ? "#16a34a" : "#ea580c"
  }

  document.getElementById("cropName").textContent = result.crop
  document.getElementById("diseaseName").textContent = result.disease
  document.getElementById("scientificName").textContent = result.scientificName

  const statusBadge = document.getElementById("statusBadge")
  statusBadge.textContent = result.status === "healthy" ? "Healthy Crop" : "Disease Detected"
  statusBadge.className = `status-badge ${result.status}` + (isFlagged ? " uncertain" : "")

  const idCard = document.getElementById("identificationCard")
  if (isFlagged) {
    idCard.classList.add("uncertain-highlight")
  } else {
    idCard.classList.remove("uncertain-highlight")
  }

  document.getElementById("affectedArea").textContent = result.affectedArea
  document.getElementById("recoveryTime").textContent = result.estimatedRecovery

  // Set symptoms
  const symptomsList = document.getElementById("symptomsList")
  symptomsList.innerHTML = result.symptoms.map((symptom) => `<li>${symptom}</li>`).join("")

  // Set treatment
  document.getElementById("remedyText").textContent = result.remedy

  // Show alternatives and low-confidence warning
  const alternativesCard = document.getElementById("alternativesCard")
  const alternativesList = document.getElementById("alternativesList")
  const uncertainText = document.getElementById("uncertainText")

  if (result.alternatives && result.alternatives.length > 0) {
    alternativesCard.style.display = "block"
    alternativesList.innerHTML = result.alternatives
      .map(
        (alt) => `<li><strong>${alt.label}</strong> — ${alt.confidence}%</li>`,
      )
      .join("")

    if (hasLowConfidence) {
      const reason = result.report.low_confidence_reason
      if (reason === "top_prediction_low") {
        uncertainText.textContent = "⚠️ LOW CONFIDENCE: Model confidence is below 50%. Please review alternatives carefully and consider re-scanning for better accuracy."
      } else if (reason === "top_2_too_close") {
        uncertainText.textContent = "⚠️ AMBIGUOUS: Top two predictions are too close. Consider re-scanning the plant from a different angle."
      }
      uncertainText.style.display = "block"
      uncertainText.style.color = "#b45309"
    } else if (result.report && result.report.ambiguous) {
      uncertainText.textContent = "Top two alternatives are different diseases of the same crop — presenting both."
      uncertainText.style.display = "block"
    } else if (result.uncertain) {
      uncertainText.textContent = "The model is uncertain. Showing top alternatives."
      uncertainText.style.display = "block"
    } else {
      uncertainText.style.display = "none"
    }
  } else {
    alternativesCard.style.display = "none"
  }

  // Render ambiguous candidate details if provided by backend
  const ambiguousCard = document.getElementById("ambiguousCard")
  const ambiguousDetails = document.getElementById("ambiguousDetails")
  if (result.report && result.report.ambiguous && result.report.ambiguous_details && result.report.ambiguous_details.length > 0) {
    ambiguousCard.style.display = "block"
    ambiguousDetails.innerHTML = result.report.ambiguous_details
      .map((c) => {
        const symptoms = (c.symptoms || []).map((s) => `<li>${s}</li>`).join("")
        return `
          <div class="ambig-item">
            <h4>${c.disease} — ${c.confidence}%</h4>
            <p><strong>Symptoms:</strong></p>
            <ul>${symptoms}</ul>
            <p><strong>Remedy:</strong> ${c.remedy || 'Not available'}</p>
            <p><strong>Prevention:</strong> ${c.prevention || 'Not available'}</p>
            <p><strong>Estimated Recovery:</strong> ${c.estimated_recovery || 'Varies'}</p>
            <p><strong>Organic Options:</strong> ${c.organic_treatment || 'Not available'}</p>
          </div>
        `
      })
      .join("<hr/>")
  } else {
    ambiguousCard.style.display = "none"
  }

  // Set chemicals
  const chemicalsCard = document.getElementById("chemicalsCard")
  const chemicalsList = document.getElementById("chemicalsList")

  if (result.chemicals.length > 0) {
    chemicalsList.innerHTML = result.chemicals
      .map(
        (chem) => `
      <div class="chemical-item">
        <h4 class="chemical-name">${chem.name}</h4>
        <div class="chemical-details">
          <div>
            <span class="chemical-label">Dosage:</span>
            <span class="chemical-value">${chem.dosage}</span>
          </div>
          <div>
            <span class="chemical-label">Application:</span>
            <span class="chemical-value">${chem.application}</span>
          </div>
        </div>
      </div>
    `,
      )
      .join("")
  } else {
    chemicalsCard.style.display = "none"
  }

  // Set organic treatment
  document.getElementById("organicText").textContent = result.organicTreatment

  // Set fertilizer
  document.getElementById("fertilizerText").textContent = result.fertilizer

  // Set prevention
  document.getElementById("preventionText").textContent = result.prevention

  // Store result for download
  window.currentResult = result

  // Show uncertain modal if needed (low confidence, uncertain, or ambiguous)
  if (hasLowConfidence || result.uncertain) {
    showUncertainModal()
  } else {
    hideUncertainModal()
  }
}

// Modal controls for uncertain predictions
function showUncertainModal() {
  const modal = document.getElementById("uncertainModal")
  if (!modal) return
  modal.classList.remove("hidden")
}

function hideUncertainModal() {
  const modal = document.getElementById("uncertainModal")
  if (!modal) return
  modal.classList.add("hidden")
}

// Attach modal button handlers
document.addEventListener("DOMContentLoaded", () => {
  const rescanBtn = document.getElementById("modalRescanBtn")
  const uploadBtn = document.getElementById("modalUploadBtn")
  const dismissBtn = document.getElementById("modalDismissBtn")

  if (rescanBtn) rescanBtn.addEventListener("click", () => { window.location.href = 'index.html' })
  if (uploadBtn) uploadBtn.addEventListener("click", () => { window.location.href = 'index.html' })
  if (dismissBtn) dismissBtn.addEventListener("click", () => { hideUncertainModal() })
})

// Download report
function downloadReport() {
  // Client-side PDF export using jsPDF and html2canvas
  const content = document.getElementById('resultsContainer') || document.body

  function ensureScript(src) {
    return new Promise((res, rej) => {
      if (document.querySelector(`script[src="${src}"]`)) return res()
      const s = document.createElement('script')
      s.src = src
      s.onload = res
      s.onerror = rej
      document.head.appendChild(s)
    })
  }

  Promise.all([
    ensureScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'),
    ensureScript('https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js')
  ]).then(() => {
    html2canvas(content, { scale: 2 }).then(canvas => {
      const imgData = canvas.toDataURL('image/png')
      const { jsPDF } = window.jspdf
      const pdf = new jsPDF('p', 'mm', 'a4')
      const imgProps = pdf.getImageProperties(imgData)
      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)
      pdf.save('plant_scan_report.pdf')
    }).catch(err => {
      console.error(err)
      alert('Failed to generate PDF')
    })
  }).catch(err => {
    console.error(err)
    alert('Failed to load PDF libraries')
  })
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  loadResults()
})

// Declare lucide variable or import it before using
const lucide = window.lucide // Assuming lucide is available globally or needs to be declared
