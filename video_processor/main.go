package main 

import (
	"context"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"strconv"

	"github.com/joho/godotenv"
	"github.com/go-redis/redis/v8"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

const (
	TelegramGroupID = -4575472838
	RedisChannel = "channel"
	UploadsDir = "../uploads"
)

type Message struct {
	TelegramID int64
	VideoPath string
}

var ctx = context.Background()

func ConvertVideo(inputPath, outputPath string) error {
	cmd := exec.Command("ffmpeg", "-i", inputPath, "-c:v", "libx264", "-crf", "23", outputPath)
	if err := cmd.Run(); err != nil {
		return err
	}
	return nil
}

func CaptureMiddleFrame(videoPath, outputPath string) error {
	cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", "thumbnail", "-frames:v", "1", outputPath)
	if err := cmd.Run(); err != nil {
		return err
	}
	return nil
}

func ProccessVideo(message Message, bot *tgbotapi.BotAPI) error {

	messageUUID := strings.TrimSuffix(filepath.Base(message.VideoPath), filepath.Ext(message.VideoPath))
	newFileName := filepath.Join(UploadsDir, messageUUID+".mp4")

	log.Printf("Получение файла: %s", newFileName)

	if err := ConvertVideo(message.VideoPath, newFileName); err != nil {
		log.Printf("Ошибка при конвертации видео %s", err)
		return err
	}
	log.Println("Видео успешно получено и сконвертировано")

	videoFile := tgbotapi.FilePath(newFileName)
	video := tgbotapi.NewVideoNote(TelegramGroupID, 0 ,videoFile)
	_, err := bot.Send(video)

	if err != nil {
		log.Printf("Ошибка отправки видео: %v", err)
		return err
	}
	log.Println("Видео успешно отправлено")
	
	return nil
}

func StreamFromRedis(rdb *redis.Client, bot *tgbotapi.BotAPI){
	pubsub := rdb.Subscribe(ctx, RedisChannel)
	defer pubsub.Close()
	ch := pubsub.Channel()

	for msg := range ch {
		log.Printf("New message %s", msg.Payload)
		payload_data := strings.SplitN(msg.Payload, ",", 2)

		if len(payload_data) != 2 {
			log.Printf("Неверный формат сообщения %s", msg.Payload)
		}

		TelegramIDInt, _ := strconv.ParseInt(payload_data[1], 10, 64)
		message := Message{TelegramID: TelegramIDInt, VideoPath: payload_data[0]}
		
		if err := ProccessVideo(message, bot); err != nil{
			log.Printf("Ошибка обработки видео %s", err)
		}
	}
}

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Ошибка получения файла .env")
	}
	telegramBotToken := os.Getenv("TELEGAM_BOT_TOKEN")

	bot, err := tgbotapi.NewBotAPI(telegramBotToken)

	if err != nil {
		log.Printf("Ошибка подключения к TelegramAPI: %v", err)
		os.Exit(1)
		return
	}

	rdb := redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
		DB: 0,
	})
	defer rdb.Close()
	log.Println("Слушаем канал в Redis")
	StreamFromRedis(rdb, bot)
}