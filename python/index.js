import express from "express";
import multer from "multer";
import { spawn, exec } from "child_process";
import fs from "fs";
import cors from "cors";
import morgan from "morgan";

const app = express();
const PORT = 3000;

app.use(
  cors({
    origin: "http://localhost:5173", // Replace with your React app's origin
    methods: ["GET", "POST"],
  })
);

app.use(morgan("tiny"));

// Configure multer for file uploads
const upload = multer({
  dest: "uploads/", // Temporary upload location
});

app.post("/sessile-drop", upload.single("image"), (req, res) => {
  console.log("Sessile Drop entered");
  const tempPath = req.file.path;
  const targetPath =
    "c:/Users/Prem/OneDrive - IIT Delhi/Desktop/GitHub/S.U.R.A.-2024/python/image_final.png";

  // Move the file to the desired location
  fs.rename(tempPath, targetPath, (err) => {
    if (err) {
      console.error("Error saving image:", err);
      return res.status(500).json({ message: "Failed to save image." });
    }
    console.log("Image uploaded successfully");
    console.log("Starting the python script");

    const pythonProcess = spawn("C://Python312//python.exe", [
      "Sessile_ossila_algo.py",
    ]);
    pythonProcess.on("error", (error) => {
      console.error("Error starting Python script:", error);
      return res.status(500).json({ output: "Error running Python script." });
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        console.error(`Python script exited with code ${code}`);
        return res
          .status(500)
          .json({ output: `Python script failed with code ${code}.` });
      }

      console.log("Python script completed successfully");
      res.json({ message: "Execution Completed" });
    });
  });
});

app.post("/pendant-drop-image", upload.single("image"), (req, res) => {
  console.log("Pendant Drop (Image) entered");

  const tempPath = req.file.path;
  const targetPath =
    "c:/Users/Prem/OneDrive - IIT Delhi/Desktop/GitHub/S.U.R.A.-2024/python/image_final.png";

  const density = req.body.density;

  if (!density) {
    console.error("Density is missing");
    fs.writeFile("Surface_Tension.txt", "Density is missing", (err) => {
      console.log("Error Occurred");
    });
    return res.status(400).json({ message: "Missing required input" });
  }

  // Step 1: Save the screenshot
  fs.rename(tempPath, targetPath, (err) => {
    if (err) {
      console.error("Error saving image:", err);
      return res.status(500).json({ message: "Failed to save image." });
    }
    console.log("Image uploaded successfully");
    console.log("Starting the python script");
    // Step 2: Write density and needle diameter to input_pendant.txt
    const inputContent = `${density}`;
    fs.writeFile("input_pendant.txt", inputContent, (err) => {
      if (err) {
        console.error("Error writing input file:", err);
        return res.status(500).json({ message: "Failed to write input file." });
      }
      console.log("Input file created successfully");

      // Step 3: Execute the Python script
      const pythonProcess = spawn("C://Python312//python.exe", [
        "pendant_ST.py",
      ]);

      pythonProcess.on("error", (error) => {
        console.error("Error starting Python script:", error);
        return res.status(500).json({ output: "Error running Python script." });
      });

      pythonProcess.on("close", (code) => {
        if (code !== 0) {
          console.error(`Python script exited with code ${code}`);
          return res
            .status(500)
            .json({ output: `Python script failed with code ${code}.` });
        }

        console.log("Python script completed successfully");
        res.json({ message: "Execution Completed" });
      });
    });
  });
});

app.post("/pendant-drop-video", upload.single("video"), (req, res) => {
  console.log("Pendant Drop (Video) entered");

  const tempPath = req.file.path;
  const targetPath =
    "c:/Users/Prem/OneDrive - IIT Delhi/Desktop/GitHub/S.U.R.A.-2024/python/video_final.mp4";

  const density = req.body.density;

  if (!density) {
    console.error("Density is missing");
    return res.status(400).json({ message: "Missing required input" });
  }

  // Step 1: Save the video
  fs.rename(tempPath, targetPath, (err) => {
    if (err) {
      console.error("Error saving image:", err);
      return res.status(500).json({ message: "Failed to save image." });
    }
    console.log("Image uploaded successfully");
    console.log("Starting the python script");
    // Step 2: Write density and needle diameter to input_pendant.txt
    const inputContent = `${density}`;
    fs.writeFile("input_pendant.txt", inputContent, (err) => {
      if (err) {
        console.error("Error writing input file:", err);
        return res.status(500).json({ message: "Failed to write input file." });
      }
      console.log("Input file created successfully");

      // Step 3: Execute the Python script
      const pythonProcess = spawn("C://Python312//python.exe", [
        "video_pendant_drop.py",
      ]);

      pythonProcess.on("error", (error) => {
        console.error("Error starting Python script:", error);
        return res.status(500).json({ output: "Error running Python script." });
      });

      pythonProcess.on("close", (code) => {
        if (code !== 0) {
          console.error(`Python script exited with code ${code}`);
          return res
            .status(500)
            .json({ output: `Python script failed with code ${code}.` });
        }

        console.log("Python script completed successfully");
        res.json({ message: "Execution Completed" });
      });
    });
  });
});

app.get("/download-results-pendant", (req, res) => {
  const csvFilePath = "Surface_Tension_data.csv";
  res.download(csvFilePath, "results.csv", (err) => {
    if (err) {
      console.error("Error serving the file:", err);
      res.status(500).send("Error serving the file.");
    }
  });
});

app.post("/hysteresis-analysis", upload.single("video"), (req, res) => {
  console.log("Hysteresis analysis entered");
  const tempPath = req.file.path; // Temporary file path from multer
  const targetPath =
    "c:/Users/Prem/OneDrive - IIT Delhi/Desktop/GitHub/S.U.R.A.-2024/python/video_final.mp4";

  // Move the video to the target location
  fs.rename(tempPath, targetPath, (err) => {
    if (err) {
      console.error("Error saving video:", err);
      return res.status(500).json({ message: "Failed to save video." });
    }

    console.log("Video uploaded successfully to:", targetPath);
    console.log("Starting the python script");
    // Run the Python script
    const pythonProcess = spawn("C://Python312//python.exe", [
      "hysteresis_final.py",
    ]);

    pythonProcess.stdout.on("data", (data) => {
      //   console.log(`Python Output: ${data.toString()}`);
    });

    pythonProcess.stderr.on("data", (data) => {
      //   console.error(`Python Error: ${data.toString()}`);
    });

    pythonProcess.on("error", (error) => {
      console.error("Error starting Python script:", error);
      return res.status(500).json({ output: "Error running Python script." });
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        console.error(`Python script exited with code ${code}`);
        return res
          .status(500)
          .json({ output: `Python script failed with code ${code}.` });
      }

      console.log("Python script completed successfully");
      console.log("CSV file created successfully");
      //   console.log(new Date().toLocaleString());
      res.json({
        message: "Execution Completed",
      });
    });
  });
});

app.get("/download-results-hysteresis", (req, res) => {
  const csvFilePath = "contact_angle_data.csv";
  res.download(csvFilePath, "results.csv", (err) => {
    if (err) {
      console.error("Error serving the file:", err);
      res.status(500).send("Error serving the file.");
    }
  });
});

app.post("/calibration", upload.single("image"), (req, res) => {
  console.log("Calibration entered");
  const tempPath = req.file.path;
  const targetPath =
    "c:/Users/Prem/OneDrive - IIT Delhi/Desktop/GitHub/S.U.R.A.-2024/python/image_final.png";

  // Move the file to the desired location
  fs.rename(tempPath, targetPath, (err) => {
    if (err) {
      console.error("Error saving image:", err);
      return res.status(500).json({ message: "Failed to save image." });
    }
    console.log("Image uploaded successfully");
    console.log("Starting the python script");

    const pythonProcess = spawn("C://Python312//python.exe", [
      "Calibration.py",
    ]);
    pythonProcess.on("error", (error) => {
      console.error("Error starting Python script:", error);
      return res.status(500).json({ output: "Error running Python script." });
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        console.error(`Python script exited with code ${code}`);
        return res
          .status(500)
          .json({ output: `Python script failed with code ${code}.` });
      }

      console.log("Python script completed successfully");
      res.json({ message: "Execution Completed" });
    });
  });
});

app.get("/sessile-drop-stream", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const interval = setInterval(() => {
    fs.readFile("Static_Contact_Angle.txt", "utf8", (err, data) => {
      if (err) {
        console.error("Error reading file:", err);
        res.write("data: Error reading file\n\n");
        clearInterval(interval);
        return;
      }
      res.write(`data: ${JSON.stringify(data)}\n\n`);
    });
  }, 1000);

  req.on("close", () => {
    clearInterval(interval);
  });
});

app.get("/pendant-drop-stream", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const interval = setInterval(() => {
    fs.readFile("Surface_Tension.txt", "utf8", (err, data) => {
      if (err) {
        console.error("Error reading file:", err);
        res.write("data: Error reading file\n\n");
        clearInterval(interval);
        return;
      }
      res.write(`data: ${JSON.stringify(data)}\n\n`);
    });
  }, 1000);

  req.on("close", () => {
    clearInterval(interval);
  });
});

app.get("/hysteresis-stream", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const interval = setInterval(() => {
    fs.readFile("Contact_Angle_Hysteresis.txt", "utf8", (err, data) => {
      if (err) {
        console.error("Error reading file:", err);
        res.write("data: Error reading file\n\n");
        clearInterval(interval);
        return;
      }
      res.write(`data: ${JSON.stringify(data)}\n\n`);
    });
  }, 1000);

  req.on("close", () => {
    clearInterval(interval);
  });
});

app.get("/calibration-stream", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const interval = setInterval(() => {
    fs.readFile("Calibration_result.txt", "utf8", (err, data) => {
      if (err) {
        console.error("Error reading file:", err);
        res.write("data: Error reading file\n\n");
        clearInterval(interval);
        return;
      }
      res.write(`data: ${JSON.stringify(data)}\n\n`);
    });
  }, 1000);

  req.on("close", () => {
    clearInterval(interval);
  });
});

app.post("/run-scrcpy", (req, res) => {
  exec("scrcpy -d", (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing scrcpy: ${error}`);
      fs.writeFile(
        "Surface_Tension.txt",
        "Connection to phone not established",
        (err) => {
          console.log("Error Occurred");
        }
      );
      fs.writeFile(
        "Static_Contact_Angle.txt",
        "Connection to phone not established",
        (err) => {
          console.log("Error Occurred");
        }
      );
      fs.writeFile(
        "Contact_Angle_Hysteresis.txt",
        "Connection to phone not established",
        (err) => {
          console.log("Error Occurred");
        }
      );
      fs.writeFile(
        "Calibration_result.txt",
        "Connection to phone not established",
        (err) => {
          console.log("Error Occurred");
        }
      );
      return res.status(500).send("Error running scrcpy");
    }
    console.log(`stdout: ${stdout}`);
    if (stderr) {
      console.log(`stderr: ${stderr}`);
    }
    res.send("scrcpy started");
  });
});

app.use((err, req, res, next) => {
  console.log("Error Occurred");
  //   console.error(err.stack);
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
