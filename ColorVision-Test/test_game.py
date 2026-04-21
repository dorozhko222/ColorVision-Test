import pygame
import sys
import json

# ========== НАСТРОЙКИ ==========
WIDTH = 800
HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# ========== ОТВЕТЫ ==========
CORRECT_ANSWERS = ["136", "2", "42", "27", "71", "7", "74", "14", "35", "74"]


# ========== ЗАГРУЗКА КАРТИНОК ==========
def load_images():
    images = []
    for i in range(1, 11):
        path = f"static/images/{i}.png"
        try:
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (400, 300))
            images.append(img)
        except:
            print(f"Ошибка: не могу загрузить {path}")
            surf = pygame.Surface((400, 300))
            surf.fill((128, 128, 128))
            images.append(surf)
    return images


def draw_text(screen, text, x, y, color=BLACK, size=36):
    font = pygame.font.Font(None, size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_text_center(screen, text, y, color=BLACK, size=36):
    font = pygame.font.Font(None, size)
    surface = font.render(text, True, color)
    x = (WIDTH - surface.get_width()) // 2
    screen.blit(surface, (x, y))


def show_result(screen, user_answers):
    correct_count = 0
    for i in range(10):
        if user_answers[i].lower() == CORRECT_ANSWERS[i].lower():
            correct_count += 1

    screen.fill(WHITE)

    draw_text_center(screen, "ТЕСТ ЗАВЕРШЁН!", 150, BLACK, 48)
    draw_text_center(screen, f"Правильных ответов: {correct_count} из 10", 250, BLACK, 36)

    if correct_count < 7:
        diagnosis = "ВНИМАНИЕ: Возможны проблемы с цветовосприятием! Рекомендуем обратиться к офтальмологу."
        draw_text_center(screen, "ВНИМАНИЕ: Возможны проблемы с цветовосприятием!", 350, RED, 28)
        draw_text_center(screen, "Рекомендуем обратиться к офтальмологу", 400, RED, 28)
    else:
        diagnosis = ("Отклонений не выявлено,"
                     "но вы можете записаться на бесплатную консультацию к офтальмологу")
        draw_text_center(screen, "Отклонений не выявлено,",300, GREEN, 32)

        draw_text_center(screen, "но вы можете записаться на бесплатную консультацию к офтальмологу", 350, GREEN, 32)

    pygame.display.flip()

    # СОХРАНЯЕМ ДИАГНОЗ В ФАЙЛ ДЛЯ САЙТА
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(diagnosis)

    # Ждём 3 секунды и закрываемся
    pygame.time.wait(3000)
    return diagnosis


def run_test():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Тест на дальтонизм")

    images = load_images()
    current_q = 0
    user_answers = []
    input_text = ""
    test_completed = False
    diagnosis = ""

    clock = pygame.time.Clock()
    running = True

    while running:
        if not test_completed and current_q < 10:
            screen.fill(WHITE)

            img = images[current_q]
            img_x = (WIDTH - img.get_width()) // 2
            img_y = 80
            screen.blit(img, (img_x, img_y))

            draw_text(screen, f"Вопрос {current_q + 1} из 10", 20, 20, BLACK, 24)
            draw_text(screen, "Что вы видите?", img_x, img_y - 40, BLACK, 30)

            input_box_x = img_x
            input_box_y = img_y + img.get_height() + 30
            pygame.draw.rect(screen, (200, 200, 200), (input_box_x, input_box_y, 300, 40))
            pygame.draw.rect(screen, BLACK, (input_box_x, input_box_y, 300, 40), 2)
            draw_text(screen, input_text, input_box_x + 5, input_box_y + 5, BLACK, 30)
            draw_text(screen, "Введите число (или 'н' если ничего не видите)", 20, HEIGHT - 40, (100, 100, 100), 20)

            pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if not test_completed and current_q < 10:
                    if event.key == pygame.K_RETURN:
                        if input_text.strip() != "":
                            user_answers.append(input_text.strip())
                            current_q += 1
                            input_text = ""

                            if current_q >= 10:
                                test_completed = True
                                diagnosis = show_result(screen, user_answers)

                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        char = event.unicode
                        if char.isalnum() or char == 'н':
                            input_text += char

        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_test()