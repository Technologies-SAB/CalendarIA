using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CalendarService.DotNet.Data;

[Table("users")]
public class User
{
    [Key]
    public int Id { get; set; }
    public string ChatId { get; set; } = null!;
    public ICollection<ConnectedAccount> Accounts { get; set; } = new List<ConnectedAccount>();
}

[Table("connected_accounts")]
public class ConnectedAccount
{
    [Key]
    public int Id { get; set; }
    public string ProviderName { get; set; } = null!;
    public string EncryptedCredentials { get; set; } = null!;
    
    [ForeignKey("User")]
    public int UserId { get; set; }
    public User Owner { get; set; } = null!;
}