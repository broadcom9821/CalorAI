//
//  calorieTrackerViewController.swift
//  CalorAI
//
//  Created by Swagat Bhowmik on 2023-11-18.
//

import UIKit

class CalorieViewController: UIViewController, UITableViewDataSource, UITableViewDelegate {

    private let tableView: UITableView = {
        let table = UITableView()
        table.register(UITableViewCell.self, forCellReuseIdentifier: "cell")
        table.separatorStyle = .none
        table.backgroundColor = .systemBackground
        return table
    }()

    private var calorieHistory: [(date: String, calories: Int, foodItem: String)] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        title = "Calorie Tracker"

        setupTableView()
        populateDummyData()
    }

    private func setupTableView() {
        tableView.dataSource = self
        tableView.delegate = self
        tableView.frame = view.bounds
        tableView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(tableView)
    }

    private func populateDummyData() {
        calorieHistory.append(("2023-11-20", 300, "Apple"))
        calorieHistory.append(("2023-11-19", 500, "Pizza"))
        calorieHistory.append(("2023-11-18", 200, "Salad"))
        tableView.reloadData()
    }

    // MARK: - UITableViewDataSource

    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return calorieHistory.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "cell", for: indexPath)
        cell.backgroundColor = .systemBackground
        cell.layer.cornerRadius = 10
        cell.layer.masksToBounds = true
        cell.selectionStyle = .none

        let entry = calorieHistory[indexPath.row]

        let titleLabel = UILabel()
        titleLabel.text = "\(entry.foodItem)"
        titleLabel.font = UIFont.boldSystemFont(ofSize: 18)
        titleLabel.textColor = .label
        titleLabel.translatesAutoresizingMaskIntoConstraints = false

        let detailsLabel = UILabel()
        detailsLabel.text = "\(entry.date) - \(entry.calories) Calories"
        detailsLabel.font = UIFont.systemFont(ofSize: 14)
        detailsLabel.textColor = .secondaryLabel
        detailsLabel.translatesAutoresizingMaskIntoConstraints = false

        cell.contentView.addSubview(titleLabel)
        cell.contentView.addSubview(detailsLabel)

        NSLayoutConstraint.activate([
            titleLabel.leadingAnchor.constraint(equalTo: cell.contentView.leadingAnchor, constant: 16),
            titleLabel.topAnchor.constraint(equalTo: cell.contentView.topAnchor, constant: 8),

            detailsLabel.leadingAnchor.constraint(equalTo: cell.contentView.leadingAnchor, constant: 16),
            detailsLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 4),
            detailsLabel.bottomAnchor.constraint(equalTo: cell.contentView.bottomAnchor, constant: -8),
        ])

        return cell
    }

    // MARK: - UITableViewDelegate

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        // Handle selection if needed
    }
}
