from constants.rimagochi_constants import *
import itertools
# Данные из файла constants.py
animals = rimagochi_animals

# Рассчитываем эффективность для каждого животного
animal_stats = []
for animal_id, animal_data in animals.items():
    #if not animal_data["params"]["rarity"] == rimagochi_rarity[31]:
        health = animal_data["params"]["health"]
        damage = animal_data["params"]["damage"]
        slots = animal_data["params"]["required_slots"]
        efficiency = (health * damage) / slots
        animal_stats.append({
            "id": animal_id,
            "name": animal_data["name"],
            "health": health,
            "damage": damage,
            "slots": slots,
            "efficiency": efficiency
        })

# Сортируем по убыванию эффективности
animal_stats.sort(key=lambda x: -x["efficiency"])

for animal_data in animal_stats:
    print(f"{animal_data['name'].replace(' ', '_')} {animal_data['damage']} {animal_data['health']} {animal_data['slots']} {animal_data['efficiency']}".replace(".", ","))
    
best_animals = {}

for animal in animal_stats:
    best_animals.setdefault(animal["slots"], animal)


the_best = [[1]]

for i in range(8):
    for animals in itertools.product(best_animals.keys(), repeat = i):
        if sum(animals) == 8:
            sum_damage = 0
            for i in animals:
                sum_damage += best_animals[i]['efficiency']*best_animals[i]['slots']
            sum_best_damage = 0
            for i in the_best[0]:
                sum_best_damage += best_animals[i]['efficiency']*best_animals[i]['slots']
            if sum_damage > sum_best_damage:
                the_best = [sorted(animals, reverse = True)]
            elif sum_damage == sum_best_damage:
                if not sorted(animals, reverse = True) in the_best:
                    the_best.append(sorted(animals, reverse = True))
                

# Вывод результатов
print("\n\nНайденные комбинации:")
i=0
for animals in the_best:
    total_slots = 0
    total_health = 0
    total_damage = 0
    total_efficiency = 0
    i+=1
    print(f"Комбинация №{i}")
    for animal in animals:
        total_slots += best_animals[animal]['slots']
        total_health += best_animals[animal]['health']
        total_damage += best_animals[animal]['damage']
        total_efficiency += best_animals[animal]['efficiency']*best_animals[animal]['slots']
        print(f"{best_animals[animal]['name']} (Здоровье: {best_animals[animal]['health']}, Урон: {best_animals[animal]['damage']}, Слоты: {best_animals[animal]['slots']})")
    print(f"\nСуммарное здоровье: {total_health}")
    print(f"Суммарный урон: {total_damage}")
    print(f"Суммарная эффективность: {total_efficiency}")
    print(f"Занято слотов: {total_slots}\n"+"--"*40)

print(max(rimagochi_animals.keys()))