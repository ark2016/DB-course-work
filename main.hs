{-# LANGUAGE OverloadedStrings     #-}
{-# LANGUAGE QuasiQuotes           #-}
{-# LANGUAGE TemplateHaskell       #-}
{-# LANGUAGE TypeFamilies          #-}
{-# LANGUAGE GADTs                 #-}
{-# LANGUAGE MultiParamTypeClasses #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}
{-# LANGUAGE DeriveGeneric         #-}

module Main where

import Web.Scotty
import Database.Persist
import Database.Persist.Sqlite
import Database.Persist.TH
import Control.Monad.IO.Class (liftIO)
import Data.Text.Lazy (Text)
import qualified Data.Text.Lazy as LT
import Data.Time (Day, UTCTime, getCurrentTime)
import Network.HTTP.Types (status201)
import GHC.Generics (Generic)

-- Определяем модели с помощью Persistent.
share [mkPersist sqlSettings, mkMigrate "migrateAll"] [persistLowerCase|
Survey
    name         Text
    season       Text Maybe
    startDate    Day
    endDate      Day
    description  Text Maybe
    deriving Show Generic
Image
    fileName        Text
    captureDateTime UTCTime
    size            Int Maybe
    hasFox          Bool
    surveyId        SurveyId
    deriving Show Generic
|]

-- Основная функция приложения.
main :: IO ()
main = do
  -- Используем SQLite-базу данных (файл "database.sqlite").
  runSqlite "database.sqlite" $ runMigration migrateAll
  -- Запуск сервера на порту 3000.
  scotty 3000 $ do

    -- GET /surveys – возвращает список всех исследований.
    get "/surveys" $ do
      surveys <- liftIO $ runSqlite "database.sqlite" $ selectList [] []
      json surveys

    -- POST /surveys – создаёт новое исследование.
    post "/surveys" $ do
      name         <- param "name"
      season       <- (param "season" >>=
                        \s -> return (if s == "" then Nothing else Just s))
                        `rescue` (\_ -> return Nothing)
      startDate    <- param "startDate"
      endDate      <- param "endDate"
      description  <- (param "description" >>=
                        \d -> return (if d == "" then Nothing else Just d))
                        `rescue` (\_ -> return Nothing)
      surveyId <- liftIO $ runSqlite "database.sqlite" $
                   insert $ Survey name season startDate endDate description
      status status201
      text $ "Created Survey with ID: " <> LT.pack (show surveyId)

    -- GET /images – возвращает список всех изображений.
    get "/images" $ do
      images <- liftIO $ runSqlite "database.sqlite" $ selectList [] []
      json images

    -- POST /images – создаёт новое изображение.
    post "/images" $ do
      fileName    <- param "fileName"
      captureTime <- param "captureDateTime"  -- Ожидается формат UTCTime (например, "2025-04-10 15:30:00")
      size        <- (param "size" >>= \s -> return (if s <= 0 then Nothing else Just s))
                     `rescue` (\_ -> return Nothing)
      hasFox      <- param "hasFox"
      surveyId    <- param "surveyId"
      imageId <- liftIO $ runSqlite "database.sqlite" $
                 insert $ Image fileName captureTime size hasFox surveyId
      status status201
      text $ "Created Image with ID: " <> LT.pack (show imageId)
