import sys

# Prompt the user to choose a package to run
choice = input("В каком режиме запустить? Введите '1' для запуска в оффлайн режиме, '2' в онлайн режиме: ")

if choice == '1':
    # Run package1
    from offline_analise import run_offline

elif choice == '2':
    # Run package2
    from online_analise import run_online

else:
    print("Invalid choice. Exiting.")
    sys.exit(1)