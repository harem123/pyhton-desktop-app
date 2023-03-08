import view
import controller

if __name__ == '__main__':
    main_window = view.MainWindow()
    game_controller = controller.Game()
    main_window.mainloop()