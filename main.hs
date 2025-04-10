{-# LANGUAGE OverloadedStrings          #-}
{-# LANGUAGE QuasiQuotes                #-}
{-# LANGUAGE TemplateHaskell            #-}
{-# LANGUAGE TypeFamilies               #-}
{-# LANGUAGE GADTs                      #-}
{-# LANGUAGE MultiParamTypeClasses      #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}
{-# LANGUAGE DeriveGeneric              #-}
{-# LANGUAGE DerivingStrategies         #-} -- For deriving Show/Generic cleanly
{-# LANGUAGE StandaloneDeriving         #-} -- For deriving instances for GADTs
{-# LANGUAGE UndecidableInstances       #-} -- For deriving instances for GADTs
{-# LANGUAGE DataKinds                  #-} -- For deriving instances for GADTs
{-# LANGUAGE FlexibleInstances          #-} -- For deriving instances for GADTs

module Main where

import Web.Scotty
import Database.Persist
import Database.Persist.Sqlite
import Database.Persist.TH
import Control.Monad.IO.Class (liftIO)
import Data.Text (Text) -- Use strict Text for models typically
import qualified Data.Text.Lazy as LT
import Data.Time (Day, UTCTime, getCurrentTime)
import Network.HTTP.Types (status201, status404, status200)
import GHC.Generics (Generic)
import Data.Aeson (ToJSON, FromJSON) -- Needed for automatic JSON handling

-- Define models based on relation-ER diagram
share [mkPersist sqlSettings, mkMigrate "migrateAll"] [persistLowerCase|
Survey
    name         Text sqltype=varchar(255) -- Added explicit type for clarity
    season       Text Maybe sqltype=varchar(50)
    startDate    Day
    endDate      Day
    description  Text Maybe
    UniqueSurveyName name -- Added uniqueness constraint based on AK
    UniqueSurveyNameDate name startDate -- Added uniqueness constraint based on AK
    deriving Show Generic

Location
    name         Text sqltype=varchar(100) Primary -- Name is the PK as per diagram
    longitude    Double
    latitude     Double
    height       Double Maybe
    UniqueLocationCoords longitude latitude -- Added uniqueness constraint based on AK
    deriving Show Generic

CameraTrap
    model           Text sqltype=varchar(100)
    serialNumber    Text Maybe sqltype=varchar(100)
    installationDate Day Maybe -- Renamed from InstalationDate, made optional? Diagram implies mandatory
    removalDate     Day Maybe
    comments        Text Maybe
    locationName    LocationId -- Foreign Key to Location (references Location's 'name' PK)
    UniqueCameraTrapModelSerial model serialNumber -- Added uniqueness constraint based on AK
    deriving Show Generic

Photographer
    firstName    Text sqltype=varchar(100)
    lastName     Text sqltype=varchar(100)
    middleName   Text Maybe sqltype=varchar(100)
    team         Text Maybe sqltype=varchar(100)
    contacts     Text sqltype=varchar(255) -- Assuming contacts is a simple text field
    UniquePhotographerName firstName lastName middleName -- Added uniqueness constraint based on AK
    UniquePhotographerContacts contacts -- Added uniqueness constraint based on AK
    deriving Show Generic

Fox
    name         Text Maybe sqltype=varchar(100) -- Name might not be unique or always known
    sex          Text sqltype=varchar(10) -- e.g., 'Male', 'Female', 'Unknown'
    age          Int Maybe -- Specific age if known
    ageGroup     Text sqltype=varchar(50) -- e.g., 'Cub', 'Juvenile', 'Adult'
    "group"      Text Maybe sqltype=varchar(100) -- Social group name/id, using quotes because 'group' is keyword
    notes        Text Maybe
    -- Unique constraints based on AKs from diagram seem complex/potentially unstable (Name+Age+Group)
    -- Often a simple auto-incrementing ID (implicit above) is better unless natural keys are truly stable.
    deriving Show Generic

Image
    fileName        Text sqltype=varchar(255)
    captureDateTime UTCTime
    size            Int Maybe
    hasFox          Bool
    surveyId        SurveyId Maybe -- Made Maybe if an image might not belong to a survey? Diagram shows mandatory (1..1)
    cameraTrapId    CameraTrapId Maybe -- FK to CameraTrap (diagram shows 0..1)
    photographerId  PhotographerId Maybe -- FK to Photographer (diagram shows 0..1)
    UniqueImageFile fileName -- Added uniqueness constraint based on AK
    UniqueImageFileDateTime fileName captureDateTime -- Added uniqueness constraint based on AK
    deriving Show Generic

-- Intersection table for the Many-to-Many relationship between Fox and Image
FoxImage
    foxId    FoxId
    imageId  ImageId
    Primary foxId imageId -- Composite Primary Key
    deriving Show Generic
|]

-- Make models JSON serializable for Scotty
-- Need standalone deriving because of the GADTs used by Persistent
deriving instance Generic (Key Survey)
deriving instance Generic (Key Location)
deriving instance Generic (Key CameraTrap)
deriving instance Generic (Key Photographer)
deriving instance Generic (Key Fox)
deriving instance Generic (Key Image)
deriving instance Generic (Key FoxImage) -- Added for FoxImage Key

-- Aeson instances
instance ToJSON Survey
instance ToJSON Location
instance ToJSON CameraTrap
instance ToJSON Photographer
instance ToJSON Fox
instance ToJSON Image
instance ToJSON FoxImage

instance FromJSON Survey
instance FromJSON Location
instance FromJSON CameraTrap
instance FromJSON Photographer
instance FromJSON Fox
instance FromJSON Image
instance FromJSON FoxImage

-- We also need ToJSON/FromJSON instances for the Keys to handle them in JSON responses/requests
-- Persistent >= 2.11 provides these automatically if you import Data.Aeson.TH and use $(deriveJSON defaultOptions ''YourKeyType)
-- but for simplicity here, we might just convert keys to/from Int64 or Text in the handlers.
-- Let's rely on the automatic instances derived via Generic for now. If issues arise, manual instances might be needed.
instance ToJSON (Key Survey)
instance ToJSON (Key Location)
instance ToJSON (Key CameraTrap)
instance ToJSON (Key Photographer)
instance ToJSON (Key Fox)
instance ToJSON (Key Image)
instance ToJSON (Key FoxImage) -- Added for FoxImage Key

instance FromJSON (Key Survey)
instance FromJSON (Key Location)
instance FromJSON (Key CameraTrap)
instance FromJSON (Key Photographer)
instance FromJSON (Key Fox)
instance FromJSON (Key Image)
instance FromJSON (Key FoxImage) -- Added for FoxImage Key


-- Database connection function
runDb :: SqlPersistM a -> IO a
runDb = runSqlite "database.sqlite"

-- Main application
main :: IO ()
main = do
  runDb $ runMigration migrateAll
  putStrLn "Starting server on port 3000"
  scotty 3000 $ do

    -- GET /surveys – returns a list of all surveys.
    get "/surveys" $ do
      surveys <- liftIO $ runDb $ selectList [] []
      json surveys

    -- POST /surveys – creates a new survey.
    -- Note: For production, add validation and better error handling
    post "/surveys" $ do
      newSurvey :: Survey <- jsonData -- Expect JSON body
      surveyId <- liftIO $ runDb $ insert newSurvey
      status status201
      json $ object ["id" .= surveyId, "message" .= ("Created Survey" :: Text)]

    -- GET /images – returns a list of all images.
    get "/images" $ do
      images <- liftIO $ runDb $ selectList [] []
      json images

    -- POST /images – creates a new image.
    post "/images" $ do
       newImage :: Image <- jsonData
       imageId <- liftIO $ runDb $ insert newImage
       status status201
       json $ object ["id" .= imageId, "message" .= ("Created Image" :: Text)]

    -- GET /foxes - returns list of all foxes
    get "/foxes" $ do
        foxes <- liftIO $ runDb $ selectList [] []
        json foxes

    -- POST /foxes - creates a new fox
    post "/foxes" $ do
        newFox :: Fox <- jsonData
        foxId <- liftIO $ runDb $ insert newFox
        status status201
        json $ object ["id" .= foxId, "message" .= ("Created Fox" :: Text)]

    -- GET /cameratraps - returns list of all camera traps
    get "/cameratraps" $ do
        traps <- liftIO $ runDb $ selectList [] []
        json traps

    -- POST /cameratraps - creates a new camera trap
    post "/cameratraps" $ do
        newTrap :: CameraTrap <- jsonData
        -- **Important**: Ensure the 'locationName' provided exists! Add validation here.
        trapId <- liftIO $ runDb $ insert newTrap
        status status201
        json $ object ["id" .= trapId, "message" .= ("Created CameraTrap" :: Text)]

    -- GET /locations - returns list of all locations
    get "/locations" $ do
        locations <- liftIO $ runDb $ selectList [] []
        json locations

    -- POST /locations - creates a new location
    post "/locations" $ do
        newLocation :: Location <- jsonData
        -- Location uses 'name' as PK, so insert handles uniqueness
        liftIO $ runDb $ insert newLocation -- insert returns the key (which is the name wrapper)
        status status201
        json $ object ["name" .= locationName newLocation, "message" .= ("Created Location" :: Text)]

     -- GET /photographers - returns list of all photographers
    get "/photographers" $ do
        photographers <- liftIO $ runDb $ selectList [] []
        json photographers

    -- POST /photographers - creates a new photographer
    post "/photographers" $ do
        newPhotographer :: Photographer <- jsonData
        photogId <- liftIO $ runDb $ insert newPhotographer
        status status201
        json $ object ["id" .= photogId, "message" .= ("Created Photographer" :: Text)]


    -- === Relationship Management ===

    -- POST /images/:imageId/foxes/:foxId - Link a Fox to an Image
    post "/images/:imgId/foxes/:fxId" $ do
      imgIdParam <- param "imgId"
      fxIdParam  <- param "fxId"
      -- Convert params to Keys (requires FromJSON instance or manual parsing)
      -- For simplicity, assuming keys are Int64 represented as text
      let maybeImgId = keyFromValues <$> sequence [parseParam imgIdParam :: ActionM (Either LT.Text PersistValue)]
      let maybeFxId = keyFromValues <$> sequence [parseParam fxIdParam :: ActionM (Either LT.Text PersistValue)]

      case (maybeImgId, maybeFxId) of
          (Just (Right imgKey), Just (Right fxKey)) -> do
              -- Check if Image and Fox exist
              imgExists <- liftIO $ runDb $ exists imgKey
              foxExists <- liftIO $ runDb $ exists fxKey
              if imgExists && foxExists then do
                 -- Create the link in the FoxImage table
                 _ <- liftIO $ runDb $ insertUnique $ FoxImage fxKey imgKey
                 -- Also might want to set image.hasFox = True here
                 liftIO $ runDb $ update imgKey [ImageHasFox =. True]
                 status status201
                 text "Fox linked to Image"
              else do
                 status status404
                 text "Image or Fox not found"
          _ -> do
              status status400 -- Bad Request
              text "Invalid Image ID or Fox ID format"

    -- GET /images/:imageId/foxes - Get all Foxes linked to an Image
    get "/images/:imgId/foxes" $ do
       imgIdParam <- param "imgId"
       let maybeImgId = keyFromValues <$> sequence [parseParam imgIdParam :: ActionM (Either LT.Text PersistValue)]
       case maybeImgId of
           Just (Right imgKey) -> do
               -- Find all FoxImage entries for this image
               foxLinks <- liftIO $ runDb $ selectList [FoxImageImageId ==. imgKey] []
               -- Extract the Fox IDs
               let foxIds = map (foxImageFoxId . entityVal) foxLinks
               -- Get the actual Fox entities
               foxes <- liftIO $ runDb $ mapM get foxIds -- Gets Maybe Fox
               json $ catMaybes foxes -- Filter out any Nothings (if a fox was deleted)
           _ -> do
              status status400
              text "Invalid Image ID format"

    -- GET /foxes/:foxId/images - Get all Images linked to a Fox
    get "/foxes/:fxId/images" $ do
       fxIdParam <- param "fxId"
       let maybeFxId = keyFromValues <$> sequence [parseParam fxIdParam :: ActionM (Either LT.Text PersistValue)]
       case maybeFxId of
           Just (Right fxKey) -> do
               imageLinks <- liftIO $ runDb $ selectList [FoxImageFoxId ==. fxKey] []
               let imageIds = map (foxImageImageId . entityVal) imageLinks
               images <- liftIO $ runDb $ mapM get imageIds
               json $ catMaybes images
           _ -> do
              status status400
              text "Invalid Fox ID format"


-- Helper to parse param to PersistValue (basic implementation)
-- This assumes keys are represented as Int64
parseParam :: LT.Text -> Either LT.Text PersistValue
parseParam t = case reads (LT.unpack t) :: [(Int64, String)] of
                 [(v, "")] -> Right $ PersistInt64 v
                 _         -> Left "Invalid integer format"