//
//  HomeViewController.swift
//  CalorAI
//
//  Created by Swagat Bhowmik on 2023-11-18.
//

import UIKit

class ContainerViewController: UIViewController {
    enum MenuState{
        case opened
        case closed
    }
    private var menuState:MenuState = .closed
    let menuVC=MenuViewController()
    let homeVC=HomeViewController()
    var navVC: UINavigationController?
    lazy var calVC=CalorieViewController()
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .red
        addChildVCs()
        
    }
    private func addChildVCs(){
        //Home
        menuVC.delegate=self
        addChild(menuVC)
        view.addSubview(menuVC.view)
        menuVC.didMove(toParent: self)
        //extra code
        
        
        
        
        //ends
        
        
        //CalorieTracker
        homeVC.delegate = self
        //change home vc to vcc to replace home with calorie tracker
        let navVC=UINavigationController(rootViewController: homeVC)
        addChild(navVC)
        view.addSubview(navVC.view)
        navVC.didMove(toParent: self)
        self.navVC = navVC
        
        //Settings
        
        
    }
    
}
extension ContainerViewController: HomeViewControllerDelegate{
    
    func didTapMenuButton() {
        print("Containerviewcontroller-home")
        toggleMenu(completion: nil)
        
    }
    func toggleMenu(completion: (() -> Void)?) {
            let screenWidth = UIScreen.main.bounds.width
            let menuWidth = screenWidth * 0.4 // Adjust the multiplier as needed

            switch menuState {
            case .closed:
                print("closed")
                UIView.animate(withDuration: 0.5, delay: 0, usingSpringWithDamping: 0.8, initialSpringVelocity: 0, options: .curveEaseInOut) {
                    self.navVC?.view.frame.origin.x = menuWidth
                } completion: { [weak self] done in
                    if done {
                        self?.menuState = .opened
                    }
                }

            case .opened:
                print("opened")
                UIView.animate(withDuration: 0.5, delay: 0, usingSpringWithDamping: 0.8, initialSpringVelocity: 0, options: .curveEaseInOut) {
                    self.navVC?.view.frame.origin.x = 0
                } completion: { [weak self] done in
                    if done {
                        self?.menuState = .closed
                        DispatchQueue.main.async {
                            completion?()
                        }
                        }
            }
            
        }
        
    }
    
}
extension ContainerViewController: MenuViewControllerDelegate{
    func didSelect(menuItem: MenuViewController.MenuOptions){
        print("did select")
        
        toggleMenu{[weak self]in
            print("dfdf")
            switch menuItem{
                
            case .home:
                self?.resetToHome()
            case .calorieTracker:
                self?.addtracker()
                
            case .settings:
                break
            case .about:
                break
            }
            
        }
    }
    func addtracker(){
        let vc=calVC
        homeVC.addChild(vc)
        homeVC.view.addSubview(vc.view)
        vc.view.frame=view.frame
        vc.didMove(toParent: homeVC)
        homeVC.title=vc.title
    }
    func resetToHome(){
        calVC.view.removeFromSuperview()
        calVC.didMove(toParent: nil)
        homeVC.title="Home"
    }
}


