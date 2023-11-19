import UIKit

protocol HomeViewControllerDelegate: AnyObject {
    func didTapMenuButton()
}

class HomeViewController: UIViewController {
    weak var delegate: HomeViewControllerDelegate?

    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "CalorAI"
        label.font = UIFont.boldSystemFont(ofSize: 40)
        label.textAlignment = .center
        label.textColor = UIColor(hex: "#ECE4F7")
        return label
    }()

    private let calorieCaptionLabel: UILabel = {
        let label = UILabel()
        label.text = "Your Daily Calorie Progress"
        label.font = UIFont.systemFont(ofSize: 18)
        label.textAlignment = .center
        label.textColor = UIColor(hex: "#684691")
        return label
    }()

    private let progressBar: UIProgressView = {
        let progressView = UIProgressView(progressViewStyle: .bar)
        progressView.progressTintColor = UIColor(hex: "#391A5E")
        progressView.trackTintColor = UIColor(hex: "#A286C4")
        progressView.layer.cornerRadius = 10
        progressView.layer.masksToBounds = true
        progressView.layer.sublayers?[1].cornerRadius = 10
        return progressView
    }()

    private let trackButton: UIButton = {
        let button = UIButton()
        button.setTitle("Track Your Calories", for: .normal)
        button.titleLabel?.font = UIFont.boldSystemFont(ofSize: 20)
        button.backgroundColor = UIColor(hex: "#391A5E")
        button.layer.cornerRadius = 10
        button.addTarget(self, action: #selector(didTapTrackButton), for: .touchUpInside)
        return button
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(hex: "#190433")
        title = "Home"
        navigationItem.leftBarButtonItem = UIBarButtonItem(image: UIImage(systemName: "line.3.horizontal"), style: .done, target: self, action: #selector(didTapMenuButton))

        setupUI()
        updateProgressBar(progress: 0.5)
    }

    private func setupUI() {
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(titleLabel)
        NSLayoutConstraint.activate([
            titleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            titleLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 30)
        ])

        calorieCaptionLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(calorieCaptionLabel)
        NSLayoutConstraint.activate([
            calorieCaptionLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            calorieCaptionLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 10)
        ])

        progressBar.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(progressBar)
        NSLayoutConstraint.activate([
            progressBar.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            progressBar.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            progressBar.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            progressBar.heightAnchor.constraint(equalToConstant: 20)
        ])

        trackButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(trackButton)
        NSLayoutConstraint.activate([
            trackButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            trackButton.topAnchor.constraint(equalTo: progressBar.bottomAnchor, constant: 30),
            trackButton.widthAnchor.constraint(equalToConstant: 200),
            trackButton.heightAnchor.constraint(equalToConstant: 40)
        ])
    }

    @objc private func didTapTrackButton() {
        let uploadVC = UploadPictureViewController()
        navigationController?.pushViewController(uploadVC, animated: true)
    }

    @objc private func didTapMenuButton() {
        delegate?.didTapMenuButton()
    }

    private func updateProgressBar(progress: Float) {
        progressBar.progress = progress
    }
}

// UIColor extension for hex colors
extension UIColor {
    convenience init(hex: String, alpha: CGFloat = 1.0) {
        var hexSanitized = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        hexSanitized = hexSanitized.replacingOccurrences(of: "#", with: "")

        var rgb: UInt64 = 0

        Scanner(string: hexSanitized).scanHexInt64(&rgb)

        let red = CGFloat((rgb & 0xFF0000) >> 16) / 255.0
        let green = CGFloat((rgb & 0x00FF00) >> 8) / 255.0
        let blue = CGFloat(rgb & 0x0000FF) / 255.0

        self.init(red: red, green: green, blue: blue, alpha: alpha)
    }
}
