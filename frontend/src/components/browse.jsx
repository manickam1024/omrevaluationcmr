import React, { useState } from "react";
import JSZip from "jszip";

const Browse = () => {
  const [date, setDate] = useState("");
  const [numStudents, setNumStudents] = useState("");
  const [images, setImages] = useState([]);
  const [error, setError] = useState("");

  const handleZipUpload = async (event) => {
    const file = event.target.files[0];

    if (!file || !file.name.endsWith(".zip")) {
      alert("Please upload a valid .zip file");
      return;
    }

    try {
      const jszip = new JSZip();
      const zip = await jszip.loadAsync(file);
      const imageFiles = [];

      const entries = Object.entries(zip.files);
      for (let i = 0; i < entries.length; i++) {
        const [filename, fileData] = entries[i];
        const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(filename);

        if (!fileData.dir && isImage) {
          const blob = await fileData.async("blob");
          const url = URL.createObjectURL(blob);
          imageFiles.push({ name: filename, url });
        }

        if (i % 5 === 0) await new Promise((res) => setTimeout(res, 0));
      }

      if (imageFiles.length !== parseInt(numStudents)) {
        setError(
          `Number of images (${imageFiles.length}) does not match number of students (${numStudents}).`,
        );
        setImages([]);
      } else {
        setError("");
        setImages(imageFiles);
      }
    } catch (error) {
      console.error("ZIP extraction error:", error);
      alert("Something went wrong while extracting the ZIP.");
    }
  };

  return (
    <div className="relative min-h-screen w-full">
      {/* ✅ Background Image */}
      <div className="absolute inset-0 -z-10">
        <img
          className="h-full w-full object-cover "
          src="https://www.webdesign.org/img_articles/20925/step01.gif"
          alt=""
        />
      </div>
      {/* ✅ Form and Preview Container */}
      <div className="max-w-3xl mx-auto pt-20 px-4 opacity-70 ">
        {/* Upload Form */}
        <div className=" bg-black p-6 rounded-3xl  shadow-md space-y-4 p-14">
          <h1 className="text-xl font-bold text-center text-white ">
            Upload Attendance ZIP
          </h1>

          <div className="flex flex-col space-y-2 text-white">
            <label className="text-sm font-medium" for="date">
              Date
            </label>
            <input
              type="date"
              id="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="border rounded p-2"
            />
          </div>

          <div className="flex flex-col space-y-2 text-white">
            <label className="text-sm font-medium" for="number">
              Number of Students
            </label>
            <input
              type="number"
              id="number"
              value={numStudents}
              onChange={(e) => setNumStudents(e.target.value)}
              className="border rounded p-2"
              min="1"
            />
          </div>

          <div>
            <label className="block mb-1 font-medium text-sm text-white hover: cursor-pointer">
              Upload ZIP (Images)
            </label>
            <input
              type="file"
              accept=".zip"
              onChange={handleZipUpload}
              className="w-full bg-gray-100 rounded p-2 hover:cursor-pointer"
              disabled={!date || !numStudents}
            />
          </div>

          {error && <p className="text-red-600 text-sm text-center">{error}</p>}
        </div>

        {/* ✅ Image Preview Below Form */}
        {images.length > 0 && (
          <div>
            <div className="mt-6 bg-white  shadow p-4 max-h-[400px] overflow-y-auto">
              <h2 className="text-lg font-semibold mb-4 text-center pt-6 pb-6">
                Image Preview
              </h2>
              <div className="grid grid-cols-4 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {images.map((img, idx) => (
                  <div key={idx} className="bg-gray-50 rounded shadow p-2">
                    <img
                      src={img.url}
                      alt={img.name}
                      className="object-contain h-24 w-full"
                    />
                    <p className="text-xs text-center mt-1 truncate">
                      {img.name}
                    </p>
                  </div>
                ))}
              </div>
            </div>
            <button
              className="bg-gray-300 w-72 p-2 rounded-xl text-black font-bold hover:cursor-pointer mt-10 mb-10 ml-4"
              style={{ width: "700px" }}>
              Generate Results
            </button>{" "}
          </div>
        )}
      </div>
    </div>
  );
};

export default Browse;
