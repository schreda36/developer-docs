﻿Imports AddValueReader.MWGift45
Module Module1
    Sub Main()
        'Create Soap Client
        Dim giftSoapClient As New GiftcardSoapClient
        'Create Credentials Object
        Dim merchantCredentials As New MerchantCredentials With {
            .MerchantName = "TEST MERCHANT",
            .MerchantSiteId = "XXXXXXXX",
            .MerchantKey = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
        }
        'Create PaymentData Object
        Dim giftPaymentData As New GiftPaymentData With {
            .Source = "READER",
            .TrackData = "%B6033590009112245098^OPTICARD/OPT^64120000000000000?;6033590009112245098=64120000000000000?"
        }
        'Create Request Object
        Dim addValueRequest As New AddValueRequest With {
            .Amount = "10.00",
            .InvoiceNumber = "INV1234",
            .MerchantTransactionId = "TRAN1234"
        }
        'Process Request
        Dim giftResponse45 As GiftResponse45
        giftResponse45 = giftSoapClient.AddValue(merchantCredentials, giftPaymentData, addValueRequest)
        'Display Results
        Console.WriteLine(" Approval Status: {0} Response Message: {1} Amount Approved: {2}", giftResponse45.ApprovalStatus + vbNewLine, giftResponse45.ResponseMessage + vbNewLine, giftResponse45.Gift.ApprovedAmount + vbNewLine)
        Console.WriteLine("Press Any Key to Close")
        Console.ReadKey()
    End Sub
End Module