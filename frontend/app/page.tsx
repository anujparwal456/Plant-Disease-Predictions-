"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, Camera, Scan, Leaf, Sparkles } from "lucide-react"

// Mock disease database for simulation
const mockDiseases = [
  {
    id: 1,
    crop: "Tomato",
    disease: "Early Blight",
    confidence: 94,
    status: "diseased",
    scientificName: "Alternaria solani",
    severity: "Moderate",
    affectedArea: "Leaves and Stems",
    symptoms: [
      "Dark brown spots with concentric rings on older leaves",
      "Yellowing around the spots",
      "Premature leaf drop",
      "Stems may show dark lesions",
    ],
    remedy:
      "Apply fungicides containing chlorothalonil or mancozeb. Remove infected leaves immediately and destroy them.",
    prevention:
      "Ensure proper spacing between plants for air circulation. Avoid overhead watering. Use disease-free seeds.",
    chemicals: [
      { name: "Chlorothalonil 75% WP", dosage: "2g per liter of water", application: "Spray every 7-10 days" },
      { name: "Mancozeb 75% WP", dosage: "2.5g per liter of water", application: "Apply at first sign of disease" },
      { name: "Azoxystrobin 23% SC", dosage: "1ml per liter of water", application: "Preventive spray every 14 days" },
    ],
    fertilizer: "Use balanced NPK fertilizer (10-10-10). Apply copper-based fungicide as preventive measure.",
    organicTreatment: "Neem oil spray (5ml per liter), Baking soda solution (1 tablespoon per liter)",
    estimatedRecovery: "2-3 weeks with proper treatment",
    spreadRisk: "High - can spread rapidly in humid conditions",
  },
  {
    id: 2,
    crop: "Potato",
    disease: "Late Blight",
    confidence: 89,
    status: "diseased",
    scientificName: "Phytophthora infestans",
    severity: "Severe",
    affectedArea: "Leaves, Stems, and Tubers",
    symptoms: [
      "Water-soaked spots on leaves that turn brown",
      "White fungal growth on leaf undersides",
      "Rapid plant collapse during humid weather",
      "Tuber infection with brown rot",
    ],
    remedy:
      "Apply systemic fungicides containing metalaxyl immediately. Remove and destroy infected plants to prevent spread.",
    prevention:
      "Plant resistant varieties. Maintain proper drainage and avoid wet conditions. Apply preventive fungicides before symptoms appear.",
    chemicals: [
      { name: "Metalaxyl 8% + Mancozeb 64% WP", dosage: "2.5g per liter", application: "Spray every 7 days" },
      { name: "Cymoxanil 8% + Mancozeb 64% WP", dosage: "2g per liter", application: "Apply at disease onset" },
      { name: "Dimethomorph 50% WP", dosage: "1g per liter", application: "Use in rotation with other fungicides" },
    ],
    fertilizer: "Use potassium-rich fertilizer. Apply Bordeaux mixture preventively. Avoid excessive nitrogen.",
    organicTreatment: "Bordeaux mixture (Copper sulfate + lime), Garlic extract spray",
    estimatedRecovery: "3-4 weeks, may require replanting in severe cases",
    spreadRisk: "Very High - can destroy entire crop in days",
  },
  {
    id: 3,
    crop: "Corn",
    disease: "Healthy",
    confidence: 96,
    status: "healthy",
    scientificName: "N/A",
    severity: "None",
    affectedArea: "None",
    symptoms: ["Plant shows no signs of disease", "Healthy green foliage", "Normal growth pattern"],
    remedy: "No treatment needed. Continue regular care and monitoring.",
    prevention:
      "Maintain current practices. Monitor regularly for any signs of disease. Ensure proper nutrition and watering.",
    chemicals: [],
    fertilizer: "Continue with balanced fertilization schedule. NPK 20-20-20 for vegetative growth.",
    organicTreatment: "Compost tea application monthly for plant health",
    estimatedRecovery: "N/A - Plant is healthy",
    spreadRisk: "None",
  },
  {
    id: 4,
    crop: "Rice",
    disease: "Bacterial Leaf Blight",
    confidence: 87,
    status: "diseased",
    scientificName: "Xanthomonas oryzae",
    severity: "Moderate to Severe",
    affectedArea: "Leaves",
    symptoms: [
      "Water-soaked lesions on leaf margins",
      "Lesions turn yellow then white",
      "Bacterial ooze visible in morning",
      "Leaf curling and wilting",
    ],
    remedy:
      "Apply copper-based bactericides immediately. Remove infected leaves and improve field drainage. Use antibiotics if severe.",
    prevention: "Use disease-free seeds. Avoid excessive nitrogen fertilization. Maintain proper water management.",
    chemicals: [
      { name: "Copper Oxychloride 50% WP", dosage: "3g per liter", application: "Spray every 10 days" },
      { name: "Streptocycline (Antibiotic)", dosage: "1g per 10 liters", application: "Apply at first symptom" },
      { name: "Plantomycin", dosage: "1g per 10 liters", application: "Use with copper fungicide" },
    ],
    fertilizer:
      "Balanced NPK with emphasis on potassium. Apply zinc sulfate if deficient. Reduce nitrogen during infection.",
    organicTreatment: "Pseudomonas fluorescens treatment, Copper-based organic fungicide",
    estimatedRecovery: "2-4 weeks depending on severity",
    spreadRisk: "High - spreads through water and wind",
  },
  {
    id: 5,
    crop: "Wheat",
    disease: "Rust (Yellow Rust)",
    confidence: 92,
    status: "diseased",
    scientificName: "Puccinia striiformis",
    severity: "Moderate",
    affectedArea: "Leaves and Stems",
    symptoms: [
      "Yellow-orange pustules in stripes on leaves",
      "Reduced photosynthesis",
      "Premature leaf death",
      "Stunted grain development",
    ],
    remedy: "Apply triazole fungicides. Remove volunteer wheat plants. Use resistant varieties for next planting.",
    prevention: "Plant resistant varieties. Remove alternate hosts. Apply preventive fungicides at tillering stage.",
    chemicals: [
      { name: "Propiconazole 25% EC", dosage: "1ml per liter", application: "Spray at first sign" },
      { name: "Tebuconazole 25% EC", dosage: "1ml per liter", application: "Apply every 14 days" },
      { name: "Mancozeb 75% WP", dosage: "2g per liter", application: "Preventive application" },
    ],
    fertilizer: "Balanced NPK. Increase potassium for disease resistance. Apply sulfur-containing fertilizers.",
    organicTreatment: "Sulfur dust application, Neem oil spray with copper",
    estimatedRecovery: "3-4 weeks, yield may be affected",
    spreadRisk: "High - spreads rapidly through wind-borne spores",
  },
]

export default function PlantScanner() {
  const router = useRouter()
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [isScanning, setIsScanning] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setUploadedImage(event.target?.result as string)
        setCameraActive(false)
      }
      reader.readAsDataURL(file)
    }
  }

  const openCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        setCameraActive(true)
        setUploadedImage(null)
      }
    } catch (err) {
      console.error("Error accessing camera:", err)
      alert("Could not access camera. Please upload an image instead.")
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext("2d")
      if (context) {
        canvasRef.current.width = videoRef.current.videoWidth
        canvasRef.current.height = videoRef.current.videoHeight
        context.drawImage(videoRef.current, 0, 0)
        const imageData = canvasRef.current.toDataURL("image/png")
        setUploadedImage(imageData)
        stopCamera()
      }
    }
  }

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks()
      tracks.forEach((track) => track.stop())
      setCameraActive(false)
    }
  }

  const scanDisease = () => {
    if (!uploadedImage) {
      alert("Please upload or capture an image first!")
      return
    }

    setIsScanning(true)

    setTimeout(() => {
      const randomDisease = mockDiseases[Math.floor(Math.random() * mockDiseases.length)]

      // Store data in sessionStorage to pass to results page
      sessionStorage.setItem(
        "scanResult",
        JSON.stringify({
          ...randomDisease,
          image: uploadedImage,
          scanDate: new Date().toISOString(),
        }),
      )

      // Redirect to results page
      router.push("/results")
    }, 2500)
  }

  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/80 border-b border-green-200 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-center md:justify-start">
            <div className="flex items-center gap-3">
              {/* Custom Logo Design */}
              <div className="relative w-14 h-14">
                <div className="absolute inset-0 bg-gradient-to-br from-green-500 via-emerald-500 to-teal-600 rounded-2xl shadow-lg transform rotate-6" />
                <div className="absolute inset-0 bg-gradient-to-tr from-green-600 to-emerald-400 rounded-2xl shadow-xl flex items-center justify-center">
                  <div className="relative">
                    <Leaf className="w-8 h-8 text-white drop-shadow-lg" strokeWidth={2.5} />
                    <Sparkles className="w-3 h-3 text-yellow-300 absolute -top-1 -right-1 animate-pulse" />
                  </div>
                </div>
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-green-700 to-emerald-600 bg-clip-text text-transparent tracking-tight">
                  CropCare AI
                </h1>
                <p className="text-xs md:text-sm text-green-600 font-medium">Smart Disease Detection</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <section className="text-center mb-16 animate-fade-in">
          <h2 className="text-5xl font-bold text-green-900 mb-4 text-balance">Scan. Detect. Protect Your Crops.</h2>
          <p className="text-xl text-green-700 mb-8 max-w-2xl mx-auto text-pretty">
            Advanced AI-powered plant disease detection. Get instant diagnosis and treatment recommendations for
            healthier crops.
          </p>
          <Button
            size="lg"
            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
            onClick={() => window.scrollTo({ top: 400, behavior: "smooth" })}
          >
            <Scan className="w-5 h-5 mr-2" />
            Start Scanning
          </Button>
        </section>

        {/* Image Upload & Camera Section */}
        <Card className="mb-8 border-2 border-green-200 shadow-xl hover:shadow-2xl transition-all duration-300 bg-white/90 backdrop-blur">
          <CardHeader>
            <CardTitle className="text-2xl text-green-900 flex items-center gap-2">
              <Camera className="w-6 h-6 text-green-600" />
              Upload or Capture Plant Photo
            </CardTitle>
            <CardDescription className="text-green-600">
              Take a clear photo of the plant leaf or crop for accurate disease detection
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Upload Section */}
              <div
                className="border-2 border-dashed border-green-300 rounded-xl p-8 text-center hover:border-green-500 hover:bg-green-50/50 transition-all duration-300 cursor-pointer group"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-16 h-16 mx-auto mb-4 text-green-500 group-hover:scale-110 transition-transform duration-300" />
                <h3 className="text-lg font-semibold text-green-900 mb-2">Upload Image</h3>
                <p className="text-sm text-green-600 mb-4">Click to browse or drag & drop</p>
                <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
                <Button variant="outline" className="border-green-500 text-green-700 hover:bg-green-50 bg-transparent">
                  Choose File
                </Button>
              </div>

              {/* Camera Section */}
              <div className="border-2 border-dashed border-green-300 rounded-xl p-8 text-center hover:border-green-500 hover:bg-green-50/50 transition-all duration-300">
                <Camera className="w-16 h-16 mx-auto mb-4 text-green-500" />
                <h3 className="text-lg font-semibold text-green-900 mb-2">Use Camera</h3>
                <p className="text-sm text-green-600 mb-4">Capture a live photo</p>
                <Button
                  onClick={openCamera}
                  disabled={cameraActive}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  {cameraActive ? "Camera Active" : "Open Camera"}
                </Button>
              </div>
            </div>

            {/* Camera View */}
            {cameraActive && (
              <div className="relative rounded-xl overflow-hidden border-4 border-green-500 shadow-2xl animate-fade-in">
                <video ref={videoRef} autoPlay playsInline className="w-full h-auto max-h-96 object-cover bg-black" />
                <canvas ref={canvasRef} className="hidden" />
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                  <Button
                    onClick={capturePhoto}
                    size="lg"
                    className="bg-white text-green-700 hover:bg-green-50 shadow-lg rounded-full w-16 h-16 p-0"
                  >
                    <div className="w-12 h-12 rounded-full border-4 border-green-600" />
                  </Button>
                </div>
              </div>
            )}

            {/* Image Preview */}
            {uploadedImage && !cameraActive && (
              <div className="relative rounded-xl overflow-hidden border-4 border-green-500 shadow-2xl animate-fade-in">
                <img
                  src={uploadedImage || "/placeholder.svg"}
                  alt="Uploaded plant"
                  className="w-full h-auto max-h-96 object-contain bg-gray-50"
                />
                <div className="absolute top-4 right-4">
                  <Button
                    onClick={() => setUploadedImage(null)}
                    variant="destructive"
                    size="sm"
                    className="rounded-full"
                  >
                    ✕
                  </Button>
                </div>
              </div>
            )}

            {/* Scan Button */}
            {uploadedImage && (
              <div className="text-center animate-fade-in">
                <Button
                  onClick={scanDisease}
                  disabled={isScanning}
                  size="lg"
                  className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                >
                  {isScanning ? (
                    <>
                      <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Scanning with AI...
                    </>
                  ) : (
                    <>
                      <Scan className="w-5 h-5 mr-2" />
                      Scan for Disease
                    </>
                  )}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Scanning Progress */}
        {isScanning && (
          <Card className="mb-8 border-2 border-green-200 shadow-xl bg-gradient-to-br from-green-50 to-emerald-50 animate-fade-in">
            <CardContent className="py-12 text-center">
              <div className="w-24 h-24 mx-auto mb-6 relative">
                <div className="absolute inset-0 border-8 border-green-200 rounded-full" />
                <div className="absolute inset-0 border-8 border-green-600 border-t-transparent rounded-full animate-spin" />
                <Sparkles className="absolute inset-0 m-auto w-10 h-10 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-green-900 mb-2">Analyzing Plant Image...</h3>
              <p className="text-green-700">AI model processing deep learning analysis</p>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}
