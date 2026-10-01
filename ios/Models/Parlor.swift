import Foundation

/**
 * FED-SPA data model - mirrors data/meta/schema.json definitions.
 *
 * LicensedParlor  <- data/public/licensed.json ("parlors" array)
 * UnlicensedParlor <- decrypted subscriber envelope ("parlors" array)
 */
struct LicensedParlor: Codable, Identifiable, Hashable {
    let licenseNumber: String
    let businessName: String
    let profession: String
    let status: String
    let expirationDate: String
    let originalIssueDate: String
    let address: Address
    let county: String
    let disciplineOnFile: Bool
    let publicComplaint: Bool
    let dataAsOf: String
    let lastChecked: String
    var notes: String?

    var id: String { licenseNumber }

    enum CodingKeys: String, CodingKey {
        case licenseNumber = "license_number"
        case businessName = "business_name"
        case profession
        case status
        case expirationDate = "expiration_date"
        case originalIssueDate = "original_issue_date"
        case address
        case county
        case disciplineOnFile = "discipline_on_file"
        case publicComplaint = "public_complaint"
        case dataAsOf = "data_as_of"
        case lastChecked = "last_checked"
        case notes
    }
}

struct UnlicensedParlor: Codable, Identifiable, Hashable {
    let businessName: String
    let address: Address
    let status: String
    let lastChecked: String
    let reason: String
    let county: String

    var id: String { "\(businessName)-\(address.street)" }

    enum CodingKeys: String, CodingKey {
        case businessName = "business_name"
        case address
        case status
        case lastChecked = "last_checked"
        case reason
        case county
    }
}

struct Address: Codable, Hashable {
    let street: String
    let city: String
    let state: String
    let zip: String
}

/** Top-level document for the public tier. */
struct LicensedDocument: Codable {
    let version: Int
    let asOf: String
    let source: String
    let sourceUrl: String
    let updateFrequency: String
    let parlors: [LicensedParlor]

    enum CodingKeys: String, CodingKey {
        case version
        case asOf = "as_of"
        case source
        case sourceUrl = "source_url"
        case updateFrequency = "update_frequency"
        case parlors
    }
}

/** Top-level document for the subscriber tier (post-decryption). */
struct UnlicensedDocument: Codable {
    let version: Int
    let asOf: String
    let parlors: [UnlicensedParlor]

    enum CodingKeys: String, CodingKey {
        case version
        case asOf = "as_of"
        case parlors
    }
}
