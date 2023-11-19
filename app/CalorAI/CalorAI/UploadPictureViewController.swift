//
//  UploadPictureViewController.swift
//  CalorAI
//
//  Created by Swagat Bhowmik on 2023-11-19.
//

//
//  UploadPictureViewController.swift
//  CalorAI
//
//  Created by Swagat Bhowmik on 2023-11-19.
//

import UIKit
import AVFoundation

class UploadPictureViewController: UIViewController {

    private let captureSession = AVCaptureSession()
    private var previewLayer: AVCaptureVideoPreviewLayer!
    private var photoOutput: AVCapturePhotoOutput!
    private var capturedImage: UIImage?

    private let captureButton: UIButton = {
        let button = UIButton()
        button.setTitle("Capture", for: .normal)
        button.titleLabel?.font = UIFont.boldSystemFont(ofSize: 20)
        button.backgroundColor = .systemGreen
        button.layer.cornerRadius = 10
        button.addTarget(self, action: #selector(didTapCaptureButton), for: .touchUpInside)
        return button
    }()

    private let loadingIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.color = .white
        indicator.hidesWhenStopped = true
        return indicator
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        title = "Upload Picture"

        setupUI()
        setupCamera()
        setupLoadingIndicator()
    }

    private func setupLoadingIndicator() {
        view.addSubview(loadingIndicator)
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            loadingIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    private func setupCamera() {
        DispatchQueue.global(qos: .userInitiated).async {
            guard let captureDevice = AVCaptureDevice.default(for: .video) else {
                self.showCameraAccessError()
                return
            }

            do {
                let input = try AVCaptureDeviceInput(device: captureDevice)
                if self.captureSession.canAddInput(input) {
                    self.captureSession.addInput(input)
                }

                self.captureSession.sessionPreset = .photo

                self.photoOutput = AVCapturePhotoOutput()
                if self.captureSession.canAddOutput(self.photoOutput) {
                    self.captureSession.addOutput(self.photoOutput)
                }

                self.previewLayer = AVCaptureVideoPreviewLayer(session: self.captureSession)
                self.previewLayer.videoGravity = .resizeAspectFill

                // Ensure UI updates are on the main thread
                DispatchQueue.main.async {
                    self.configurePreviewLayer()
                }
            } catch {
                // Ensure UI updates are on the main thread
                DispatchQueue.main.async {
                    self.showCameraSetupError(error)
                }
            }
        }
    }

    private func configurePreviewLayer() {
        self.previewLayer.frame = self.view.layer.bounds
        self.view.layer.insertSublayer(self.previewLayer, at: 0)
        self.captureSession.startRunning()
    }

    private func showCameraAccessError() {
        print("Failed to access the camera.")
        // You might want to present an alert to the user
    }

    private func showCameraSetupError(_ error: Error) {
        print("Error setting up camera input: \(error.localizedDescription)")
        // You might want to present an alert to the user
    }

    private func setupUI() {
        captureButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(captureButton)
        NSLayoutConstraint.activate([
            captureButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            captureButton.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20),
            captureButton.widthAnchor.constraint(equalToConstant: 200),
            captureButton.heightAnchor.constraint(equalToConstant: 40)
        ])
    }

    @objc private func didTapCaptureButton() {
        let photoSettings = AVCapturePhotoSettings()
        photoOutput.capturePhoto(with: photoSettings, delegate: self)
    }

    private func presentImagePopup(withFoodLabel foodLabel: String) {
        guard let capturedImage = capturedImage else {
            return
        }

        let popupViewController = CapturedImagePopupViewController(image: capturedImage, foodLabel: foodLabel)
        popupViewController.modalPresentationStyle = .overFullScreen

        // Show loading indicator while waiting for API response
        loadingIndicator.startAnimating()

        present(popupViewController, animated: true) {
            // Hide loading indicator when the popup is presented
            self.loadingIndicator.stopAnimating()
        }
    }
}

extension UploadPictureViewController: AVCapturePhotoCaptureDelegate {
    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        guard let imageData = photo.fileDataRepresentation(),
              let capturedImage = UIImage(data: imageData) else {
            print("Error capturing photo.")
            return
        }

        self.capturedImage = capturedImage
        fetchFoodLabelFromAPI { foodLabel in
            DispatchQueue.main.async {
                self.presentImagePopup(withFoodLabel: foodLabel)
            }
        }
    }

    private func fetchFoodLabelFromAPI(completion: @escaping (String) -> Void) {
        guard let capturedImage = capturedImage else {
            print("Error: Captured image is nil.")
            return
        }

        guard let imageData = capturedImage.jpegData(compressionQuality: 1.0) else {
            print("Error: Unable to convert image to JPEG data.")
            return
        }

        let boundary = "YOUR_BOUNDARY"

        let apiUrl = "https://calorai-4.onrender.com/predict"
        var request = URLRequest(url: URL(string: apiUrl)!)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)

        request.httpBody = body

        // Print the complete URLRequest before sending
        if let url = request.url?.absoluteString,
           let httpMethod = request.httpMethod,
           let headers = request.allHTTPHeaderFields,
           let body = request.httpBody,
           let requestString = String(data: body, encoding: .utf8) {
            print("Complete API Request:")
            print("URL: \(url)")
            print("Method: \(httpMethod)")
            print("Headers: \(headers)")
            print("Body: \(requestString)")
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: \(error.localizedDescription)")
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                print("Error: No HTTP response")
                return
            }

            print("HTTP Status Code: \(httpResponse.statusCode)")

            guard let data = data else {
                print("Error: No data in the response")
                return
            }

            do {
                let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any]
                print("API Response: \(json ?? [:])")

                if let foodLabel = json?["label"] as? String {
                    print(foodLabel)
                    completion(foodLabel)
                } else {
                    print("Error: Missing 'label' in the API response")
                    completion("Unknown")
                }
            } catch {
                print("Error parsing API response: \(error.localizedDescription)")
                completion("Unknown")
            }
        }.resume()

    }
}

class CapturedImagePopupViewController: UIViewController {

    private let imageView: UIImageView
    private let labelTextField: UITextField
    private let confirmButton: UIButton
    private let retakeButton: UIButton
    private let foodLabel: String

    init(image: UIImage, foodLabel: String) {
        self.imageView = UIImageView(image: image)
        self.labelTextField = UITextField()
        self.confirmButton = UIButton()
        self.retakeButton = UIButton()
        self.foodLabel = foodLabel

        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()

        view.backgroundColor = UIColor.black.withAlphaComponent(0.7)

        let titleLabel = UILabel()
        titleLabel.text = "Delicious choice! Your food has been identified as"
        titleLabel.textColor = .white
        titleLabel.textAlignment = .center
        titleLabel.numberOfLines = 0
        titleLabel.translatesAutoresizingMaskIntoConstraints = false

        let foodLabelLabel = UILabel()
        foodLabelLabel.text = foodLabel  // Display the food label
        foodLabelLabel.textColor = .systemGreen
        foodLabelLabel.textAlignment = .center
        foodLabelLabel.font = UIFont.boldSystemFont(ofSize: 20)
        foodLabelLabel.numberOfLines = 0
        foodLabelLabel.translatesAutoresizingMaskIntoConstraints = false

        imageView.contentMode = .scaleAspectFit
        imageView.translatesAutoresizingMaskIntoConstraints = false

        // Set a maximum height constraint for the imageView
        let maxHeightConstraint = NSLayoutConstraint(item: imageView, attribute: .height, relatedBy: .lessThanOrEqual, toItem: nil, attribute: .notAnAttribute, multiplier: 1, constant: 200)
        imageView.addConstraint(maxHeightConstraint)

        labelTextField.placeholder = "Enter additional label (optional)"
        labelTextField.borderStyle = .roundedRect
        labelTextField.translatesAutoresizingMaskIntoConstraints = false

        confirmButton.setTitle("Confirm", for: .normal)
        confirmButton.backgroundColor = .systemGreen
        confirmButton.layer.cornerRadius = 10
        confirmButton.addTarget(self, action: #selector(confirmButtonTapped), for: .touchUpInside)
        confirmButton.translatesAutoresizingMaskIntoConstraints = false

        retakeButton.setTitle("Retake", for: .normal)
        retakeButton.backgroundColor = .systemRed
        retakeButton.layer.cornerRadius = 10
        retakeButton.addTarget(self, action: #selector(retakeButtonTapped), for: .touchUpInside)
        retakeButton.translatesAutoresizingMaskIntoConstraints = false

        let stackView = UIStackView(arrangedSubviews: [titleLabel, foodLabelLabel, imageView, labelTextField, confirmButton, retakeButton])
        stackView.axis = .vertical
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(stackView)

        NSLayoutConstraint.activate([
            stackView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            stackView.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    @objc private func confirmButtonTapped() {
        if !foodLabel.isEmpty {
            labelTextField.text = "Delicious choice! Your food has been identified as \(foodLabel)"
        } else {
            labelTextField.text = "Delicious choice! Your food has been identified as a delightful dish"
        }
        dismiss(animated: true, completion: nil)
    }

    @objc private func retakeButtonTapped() {
        print("Retake tapped")
        dismiss(animated: true, completion: nil)
    }
}
